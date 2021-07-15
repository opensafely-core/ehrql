import sqlalchemy


BACKENDS = {}


def register_backend(backend_class):
    BACKENDS[backend_class.backend_id] = backend_class


class BaseBackend:

    backend_id = NotImplemented
    query_engine_class = NotImplemented
    patient_join_column = NotImplemented

    tables = set()

    def __init_subclass__(cls, **kwargs):
        assert cls.backend_id != NotImplemented
        assert cls.query_engine_class != NotImplemented
        assert cls.patient_join_column != NotImplemented

        # Register each Backend by its id so we can identify it from an environment variable
        register_backend(cls)
        # Make sure each Backend knows what its tables are
        for name, value in vars(cls).items():
            if isinstance(value, SQLTable):
                cls.tables.add(name)
                value.columns["patient_id"] = Column("int", cls.patient_join_column)

    def __init__(self, database_url):
        self.database_url = database_url

    def get_table_expression(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"Unknown table '{table_name}'")
        table = getattr(self, table_name)
        table_expression = table.get_query()
        table_expression = table_expression.alias(table_name)
        return table_expression


class SQLTable:
    def __init__(self, *, columns=None, source=None):
        self.name = source
        self.columns = columns or {}

    def get_query(self):
        columns = []
        for name, column in self.columns.items():
            source = column.source
            columns.append(sqlalchemy.literal_column(source).label(name))
        query = sqlalchemy.select(columns).select_from(sqlalchemy.table(self.name))
        return query


class Column:
    def __init__(self, column_type, source=None, system=None):
        self.type = column_type
        self.source = source
        self.system = system
