import re

from ehrql.permissions import parse_permissions
from ehrql.query_language import get_tables_from_namespace
from ehrql.query_model import nodes as qm


class ValidationError(Exception): ...


class BaseBackend:
    display_name = None
    implements = ()
    internal_tables = {}

    def __init__(self, environ=None):
        self.environ = environ or {}
        self.permissions = parse_permissions(self.environ)

    def modify_dsn(self, dsn: str | None) -> str | None:
        """
        This hook gives backends the option to modify the DSN before it's passed to the
        query engine, including removing and storing any special-case config values
        """
        return dsn

    def modify_dataset(self, dataset: qm.Dataset) -> qm.Dataset:
        """
        This hook gives backends the option to modify the dataset before running it
        """
        return dataset

    def modify_inline_table_args(self, columns, rows):
        """
        This hook gives backends the option to modify inline table arguments
        """
        return columns, rows

    def modify_query_pre_reify(self, query):
        """
        This hook gives backends the option to modify queries before they are
        passed to `reify_query`
        """
        return query

    def get_exit_status_for_exception(self, exception):
        return None


class SQLBackend(BaseBackend):
    query_engine_class = None
    patient_join_column = None
    tables = None

    def __init_subclass__(cls, **kwargs):
        assert cls.display_name is not None
        assert cls.query_engine_class is not None
        assert cls.patient_join_column is not None

        # Make sure each Backend knows what its tables are
        cls.tables = {}
        for name, value in vars(cls).items():
            if isinstance(value, SQLTable):
                cls._init_table(value)
                cls.tables[name] = value

        # Construct an instance in order to validate it
        instance = cls()
        for table_namespace in instance.implements:
            instance.validate_against_table_namespace(table_namespace)

    @classmethod
    def _init_table(cls, table):
        """
        Initialises the table
        Args:
            table: SQLTable Object
        """
        table.learn_patient_join(cls.patient_join_column)

    def validate_against_table_namespace(self, table_namespace):
        for attr, ql_table in get_tables_from_namespace(table_namespace):
            table = ql_table._qm_node
            if table.name not in self.tables:
                raise ValidationError(
                    f"{self.__class__} does not implement table '{table.name}' from "
                    f"{table_namespace}.{attr}"
                )

            table_def = self.tables[table.name]
            try:
                table_def.validate_against_table_schema(
                    backend=self, schema=table.schema
                )
            except ValidationError as e:
                # Wrap error message to indicate source
                raise ValidationError(
                    f"{self.__class__}.{table.name} does not match {table_namespace}.{attr}, {e}"
                ) from e

    def get_table_definition(self, table_node):
        return self.tables[table_node.name]

    def column_kwargs_for_type(self, type_):
        return self.query_engine_class.column_kwargs_for_type(type_)

    def get_query_engine(self, dsn):
        return self.query_engine_class(dsn, backend=self, environ=self.environ)


class SQLTable:
    def learn_patient_join(self, source):
        self.patient_join_column = source

    def validate_against_table_schema(self, backend, schema):
        raise NotImplementedError()


class MappedTable(SQLTable):
    def __init__(self, source, columns, schema=None):
        self.source_table_name = source
        self.column_map = columns
        # Not to be confused with the schema which defines the column names and types
        self.db_schema_name = schema

    def validate_against_table_schema(self, backend, schema):
        missing = set(schema.column_names) - set(self.column_map)
        if missing:
            raise ValidationError(f"missing columns: {', '.join(missing)}")

    def get_db_column_name(self, name):
        if name == "patient_id":
            return self.column_map.get(name, self.patient_join_column)
        else:
            return self.column_map[name]


class QueryTable(SQLTable):
    def __init__(self, query, materialize=False, implementation_notes=None):
        self.query = query
        self.materialize = materialize
        self.implementation_notes = implementation_notes or {}
        self._query_builder = None

    @classmethod
    def from_function(cls, fn=None, materialize=False):
        instance = cls(query=None, materialize=materialize)

        def wrapper(fn):
            instance._query_builder = fn
            return instance

        if fn is not None:
            return wrapper(fn)
        else:
            return wrapper

    def get_query(self, backend):
        if self._query_builder is not None:
            return self._query_builder(backend)
        else:
            return self.query

    def validate_against_table_schema(self, backend, schema):
        # This is a very crude form of validation: we just check that the SQL string
        # contains each of the column names as words. But without actually executing the
        # SQL we can't know what it returns
        query = self.get_query(backend)
        columns = ["patient_id", *schema.column_names]
        missing = [
            name for name in columns if not re.search(rf"\b{re.escape(name)}\b", query)
        ]
        if missing:
            raise ValidationError(
                f"SQL does not reference columns: {', '.join(missing)}"
            )


class DefaultSQLBackend(BaseBackend):
    """
    This is used as the default backend in all SQL-based query engines when no backend
    is supplied. It assumes that the tables, columns and types specified in the query
    model exactly match the database schema and therefore no translation needs to be
    done. This significantly simplifies testing of the query engines.
    """

    def __init__(self, query_engine_class):
        self.query_engine_class = query_engine_class
        super().__init__()

    def get_table_definition(self, node):
        # We create a MappedTable which simply maps each column name in the supplied
        # schema to itself and then use the default patient join column of `patient_id`
        table = MappedTable(
            source=node.name,
            columns={col_name: col_name for col_name in node.schema.column_names},
        )
        table.learn_patient_join("patient_id")
        return table

    def column_kwargs_for_type(self, type_):
        return self.query_engine_class.column_kwargs_for_type(type_)
