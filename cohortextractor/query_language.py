def table(name):
    return Table(name)


class Table:
    def __init__(self, name):
        self.name = name

    def get(self, column):
        return Column(table=self, name=column)

    def filter(self, *args, **kwargs):  # noqa: A003
        column, value = list(kwargs.items())[0]
        return FilteredTable(source=self, column=column, operator="__eq__", value=value)

    def latest(self, *args):
        return self.last_by("date")

    def last_by(self, *columns):
        assert columns
        return Row(source=self, sort_columns=columns, descending=False)


class FilteredTable(Table):
    def __init__(self, source, column, operator, value):
        self.source = source
        self.column = column
        self.operator = operator
        self.value = value


class Column:
    def __init__(self, table, name) -> None:
        self._table = table
        self.column = name

    @property
    def table(self):
        return self._table.name


class Row:
    def __init__(self, source, sort_columns, descending=False):
        self.source = source
        self.sort_columns = sort_columns
        self.descending = descending

    def get(self, column):
        return ValueFromRow(source=self, column=column)


class ValueFromRow:
    def __init__(self, source, column):
        self.source = source
        self.column = column
