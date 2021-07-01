import sqlalchemy


BACKENDS = {}


def register_backend(backend_class):
    BACKENDS[backend_class.backend_id] = backend_class


class BaseBackend:

    query_engine_class = NotImplemented
    backend_id = NotImplemented

    def __init_subclass__(cls, **kwargs):
        # Register each Backend by its id so we can identify it from an environment variable
        register_backend(cls)
        # Make sure each Backend knows what its tables are
        cls.tables = set()
        for name, value in vars(cls).items():
            if isinstance(value, BackendTable):
                cls.tables.add(name)

    def __init__(self, database_url):
        self.database_url = database_url

    def get_table_expression(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"Unknown table '{table_name}'")
        table = getattr(self, table_name)
        table_expression = table.get_query()
        table_expression = table_expression.alias(table_name)
        return table_expression


class BackendTable:
    ...


class SQLTable(BackendTable):
    def __init__(self, *, columns, source=None):
        if "patient_id" not in columns:
            columns["patient_id"] = Column("int", "PatientId")
        self.name = source
        self.columns = columns

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
