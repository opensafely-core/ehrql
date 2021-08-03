import sqlalchemy


BACKENDS = {}


def register_backend(backend_class):
    BACKENDS[backend_class.backend_id] = backend_class


class BaseBackend:
    backend_id = NotImplemented
    query_engine_class = NotImplemented
    patient_join_column = NotImplemented

    tables = None

    def __init_subclass__(cls, **kwargs):
        assert cls.backend_id != NotImplemented
        assert cls.query_engine_class != NotImplemented
        assert cls.patient_join_column != NotImplemented

        # Register each Backend by its id so we can identify it from an environment variable
        register_backend(cls)
        # Make sure each Backend knows what its tables are
        cls.tables = set()
        for name, value in vars(cls).items():
            if isinstance(value, SQLTable):
                cls.tables.add(name)
                value.learn_patient_join(cls.patient_join_column)

    def __init__(self, database_url):
        self.database_url = database_url

    def get_table_expression(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"Unknown table '{table_name}'")
        table = getattr(self, table_name)
        return table.get_query().alias(table_name)


class SQLTable:
    def learn_patient_join(self, source):
        raise NotImplementedError()


class MappedTable(SQLTable):
    def __init__(self, source, columns):
        self.source = source
        self._columns = columns

    def learn_patient_join(self, source):
        self._columns["patient_id"] = Column("integer", source)

    def get_query(self):
        columns = [
            self._make_column(name, column.source)
            for name, column in self._columns.items()
        ]
        query = sqlalchemy.select(columns).select_from(sqlalchemy.table(self.source))
        return query

    @staticmethod
    def _make_column(name, source):
        return sqlalchemy.literal_column(source).label(name)


class QueryTable(SQLTable):
    def __init__(self, query, columns):
        self.query = query
        self._columns = columns

    def learn_patient_join(self, source):
        self._columns["patient_id"] = Column("integer")

    def get_query(self):
        columns = [sqlalchemy.literal_column(column) for column in self._columns.keys()]
        return sqlalchemy.text(self.query).columns(*columns)


class Column:
    def __init__(self, column_type, source=None, system=None):
        self.type = column_type
        self.source = source
        self.system = system
