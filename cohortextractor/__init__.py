def table(name):
    return Table(name)


class Table:
    def __init__(self, name):
        self.name = name

    def get(self, column):
        return Column(table=self, name=column)


class Column:
    def __init__(self, table, name) -> None:
        self._table = table
        self.column = name

    @property
    def table(self):
        return self._table.name
