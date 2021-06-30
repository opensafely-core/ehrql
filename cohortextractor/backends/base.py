import sqlalchemy


class BaseBackend:
    def __init_subclass__(cls, **kwargs):
        cls.tables = set()
        for name, value in vars(cls).items():
            if isinstance(value, BackendTable):
                cls.tables.add(name)

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
