from __future__ import annotations

import sqlalchemy

from ..query_engines.base_sql import BaseSQLQueryEngine
from ..sqlalchemy_types import TYPES_BY_NAME

# Mutable global for storing registered backends
BACKENDS = {}


def register_backend(backend_class):
    BACKENDS[backend_class.backend_id] = backend_class


class BaseBackend:
    backend_id: str
    query_engine_class: type[BaseSQLQueryEngine]
    patient_join_column: str

    tables = None

    def __init_subclass__(cls, **kwargs):
        assert cls.backend_id is not None
        assert cls.query_engine_class is not None
        assert cls.patient_join_column is not None

        # Register each Backend by its id so we can identify it from an environment variable
        register_backend(cls)
        # Make sure each Backend knows what its tables are
        cls.tables = set()
        for name, value in vars(cls).items():
            if isinstance(value, SQLTable):
                cls._init_table(value)
                cls.tables.add(name)

    @classmethod
    def _init_table(cls, table: SQLTable) -> None:
        """
        Initialises the table
        Args:
            table: SQLTable Object
        """
        table.learn_patient_join(cls.patient_join_column)

    def __init__(self, database_url, temporary_database=None):
        self.database_url = database_url
        self.temporary_database = temporary_database

    @classmethod
    def validate_contract(cls, name, table):
        """
        Validates that the table correctly implements the contract it
        claims to, if any
        Args:
            name: Name of table
            table: SQLTable Subclass
        """
        contract = table.implements
        if contract:
            contract.validate_implementation(cls, name, table)

    @classmethod
    def validate_all_contracts(cls) -> None:
        """
        Loops through all the tables in a backend and validates that
        each one meets any contract that it claims to implement
        """
        for name, value in vars(cls).items():
            if isinstance(value, SQLTable):
                cls.validate_contract(name, value)

    def get_table_expression(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"Unknown table '{table_name}'")
        table = getattr(self, table_name)
        return table.get_query().alias(table_name)


class SQLTable:
    def learn_patient_join(self, source):
        raise NotImplementedError()

    def _make_columns(self):
        return [
            self._make_column(name, column) for name, column in self.columns.items()
        ]

    def _make_column(self, name, column):
        source = column.source or name
        type_ = TYPES_BY_NAME[column.type].value
        sql_column = sqlalchemy.Column(source, type_)
        if source != name:
            sql_column = sql_column.label(name)
        return sql_column


class MappedTable(SQLTable):
    def __init__(self, source, columns, schema=None, implements=None):
        self.source = source
        self.columns = columns
        self._schema = schema
        self.implements = implements

    def learn_patient_join(self, source):
        if "patient_id" not in self.columns:
            self.columns["patient_id"] = Column("integer", source)

    def get_query(self):
        columns = self._make_columns()
        query = sqlalchemy.select(columns).select_from(
            sqlalchemy.table(self.source, schema=self._schema)
        )
        return query


class QueryTable(SQLTable):
    def __init__(self, query, columns, implements=None):
        self.query = query
        self.columns = columns
        self.implements = implements

    def learn_patient_join(self, source):
        if "patient_id" not in self.columns:
            self.columns["patient_id"] = Column("integer")

    def get_query(self):
        columns = self._make_columns()
        return sqlalchemy.text(self.query).columns(*columns)


class Column:
    def __init__(self, column_type, source=None, system=None):
        self.type = column_type
        self.source = source
        self.system = system
