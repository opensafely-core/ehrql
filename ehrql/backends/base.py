import re

import sqlalchemy

from ehrql.permissions import parse_permissions
from ehrql.query_language import get_tables_from_namespace
from ehrql.query_model import nodes as qm


class ValidationError(Exception): ...


class BaseBackend:
    display_name = None
    implements = ()

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

    def get_table_expression(self, table_name, schema):
        """
        Gets SQL expression for a table
        Args:
            table_name: Name of Table
            schema: a TableSchema
        Returns:
            A SQLAlchmey TableClause
        Raises:
            ValueError: If unknown table passed in
        """
        return self.tables[table_name].get_expression(
            backend=self, table_name=table_name, schema=schema
        )

    def column_kwargs_for_type(self, type_):
        return self.query_engine_class.column_kwargs_for_type(type_)


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

    def get_expression(self, backend, table_name, schema):
        patient_id_column = self.column_map.get("patient_id", self.patient_join_column)
        return sqlalchemy.table(
            self.source_table_name,
            sqlalchemy.Column(patient_id_column, key="patient_id"),
            *[
                sqlalchemy.Column(
                    self.column_map[name],
                    key=name,
                    **backend.column_kwargs_for_type(type_),
                )
                for (name, type_) in schema.column_types
            ],
            schema=self.db_schema_name,
        )


class QueryTable(SQLTable):
    def __init__(self, query, implementation_notes=None):
        self.query = query
        self.implementation_notes = implementation_notes or {}

    @classmethod
    def from_function(cls, fn):
        instance = cls(query=None)
        instance.get_query = fn
        return instance

    def get_query(self, backend):
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

    def get_expression(self, backend, table_name, schema):
        columns = [sqlalchemy.Column("patient_id")]
        columns.extend(
            sqlalchemy.Column(name, **backend.column_kwargs_for_type(type_))
            for (name, type_) in schema.column_types
        )
        query = sqlalchemy.text(self.get_query(backend)).columns(*columns)
        return query.alias(table_name)


class DefaultSQLBackend(BaseBackend):
    def __init__(self, query_engine_class):
        self.query_engine_class = query_engine_class
        super().__init__()

    def get_table_expression(self, table_name, schema):
        """
        Returns a SQLAlchemy Table object matching the supplied name and schema
        """
        return sqlalchemy.table(
            table_name,
            sqlalchemy.Column("patient_id"),
            *[
                sqlalchemy.Column(name, **self.column_kwargs_for_type(type_))
                for (name, type_) in schema.column_types
            ],
        )

    def column_kwargs_for_type(self, type_):
        return self.query_engine_class.column_kwargs_for_type(type_)
