import re

import sqlalchemy

from databuilder.query_language import BaseFrame
from databuilder.sqlalchemy_types import type_from_python_type


class ValidationError(Exception):
    ...


class BaseBackend:
    query_engine_class = None
    patient_join_column = None
    tables = None
    implements = ()

    def __init_subclass__(cls, **kwargs):
        assert cls.query_engine_class is not None
        assert cls.patient_join_column is not None

        # Make sure each Backend knows what its tables are
        cls.tables = {}
        for name, value in vars(cls).items():
            if isinstance(value, SQLTable):
                cls._init_table(value)
                cls.tables[name] = value

        for table_namespace in cls.implements:
            cls.validate_against_table_namespace(table_namespace)

    @classmethod
    def _init_table(cls, table):
        """
        Initialises the table
        Args:
            table: SQLTable Object
        """
        table.learn_patient_join(cls.patient_join_column)

    @classmethod
    def validate_against_table_namespace(cls, table_namespace):
        for attr, table in get_tables_from_namespace(table_namespace):
            if table.name not in cls.tables:
                raise ValidationError(
                    f"{cls} does not implement table '{table.name}' from "
                    f"{table_namespace}.{attr}"
                )

            table_def = cls.tables[table.name]
            try:
                table_def.validate_against_table_schema(table.schema)
            except ValidationError as e:
                # Wrap error message to indicate source
                raise ValidationError(
                    f"{cls}.{table.name} does not match {table_namespace}.{attr}, {e}"
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
        return self.tables[table_name].get_expression(table_name, schema)


class SQLTable:
    def learn_patient_join(self, source):
        self.patient_join_column = source

    def validate_against_table_schema(self, schema):
        raise NotImplementedError()


class MappedTable(SQLTable):
    def __init__(self, source, columns, schema=None):
        self.source_table_name = source
        self.column_map = columns
        # Not to be confused with the schema which defines the column names and types
        self.db_schema_name = schema

    def validate_against_table_schema(self, schema):
        missing = set(schema) - set(self.column_map)
        if missing:
            raise ValidationError(f"missing columns: {', '.join(missing)}")

    def get_expression(self, table_name, schema):
        patient_id_column = self.column_map.get("patient_id", self.patient_join_column)
        return sqlalchemy.table(
            self.source_table_name,
            sqlalchemy.Column(patient_id_column, key="patient_id"),
            *[
                sqlalchemy.Column(
                    self.column_map[name], key=name, type_=type_from_python_type(type_)
                )
                for (name, type_) in schema.items()
            ],
            schema=self.db_schema_name,
        )


class QueryTable(SQLTable):
    def __init__(self, query, implementation_notes=None):
        self.query = query
        self.implementation_notes = implementation_notes or {}

    def validate_against_table_schema(self, schema):
        # This is a very crude form of validation: we just check that the SQL string
        # contains each of the column names as words. But without actually executing the
        # SQL we can't know what it returns
        columns = ["patient_id", *schema.keys()]
        missing = [
            name
            for name in columns
            if not re.search(rf"\b{re.escape(name)}\b", self.query)
        ]
        if missing:
            raise ValidationError(
                f"SQL does not reference columns: {', '.join(missing)}"
            )

    def get_expression(self, table_name, schema):
        columns = [sqlalchemy.Column("patient_id")]
        columns.extend(
            sqlalchemy.Column(name, type_=type_from_python_type(type_))
            for (name, type_) in schema.items()
        )
        query = sqlalchemy.text(self.query).columns(*columns)
        return query.alias(table_name)


class DefaultBackend:
    def get_table_expression(self, table_name, schema):
        """
        Returns a SQLAlchemy Table object matching the supplied name and schema
        """
        return sqlalchemy.table(
            table_name,
            sqlalchemy.Column("patient_id"),
            *[
                sqlalchemy.Column(name, type_=type_from_python_type(type_))
                for (name, type_) in schema.items()
            ],
        )


def get_tables_from_namespace(namespace):
    """
    Get all query model SelectTable/SelectPatientTable objects referenced by any Frames
    contained in `namespace`
    """
    for attr, value in vars(namespace).items():
        if isinstance(value, BaseFrame):
            yield attr, value.qm_node
