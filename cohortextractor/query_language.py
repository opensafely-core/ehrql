from collections import namedtuple


_OPERATOR_MAPPING = {
    "equals": "__eq__",
    "not_equals": "__ne__",
    "less_than": "__lt__",
    "less_than_or_equals": "__le__",
    "greater_than": "__gt__",
    "greater_than_or_equals": "__ge__",
    "on_or_before": "__le__",
    "on_or_after": "__ge__",
    "is_in": "in_",
    "not_in": "not_in",
}


def table(name):
    return Table(name)


def category_group(source, comparison, value):
    return CategoryGroup(source, _OPERATOR_MAPPING[comparison], value)


class QueryNode:
    pass


class Table(QueryNode):
    def __init__(self, name):
        self.name = name

    def get(self, column):
        return Column(source=self, column=column)

    def filter(self, *args, **kwargs):  # noqa: A003
        """
        args: max 1 arg, a field name (str)
        kwargs:
           - either one or more "equals" filters, or
           - k=v pairs of operator=filter conditions to be applied to a single field (the arg)
        Filter formats:
        - equals: `filter(a=b, c=d)` (allows multiple in one query)
        - between: `filter("a", between=[start_date_column, end_date_column]})`
        - others: `filter("a", less_than=b)`
        """
        if not args:
            # No args; this is an equals filter
            assert kwargs
            node = self
            # apply each of the equals filters, converted into a field arg and single equals kwarg
            for field, value in kwargs.items():
                node = node.filter(field, equals=value)
            return node
        elif len(kwargs) > 1:
            # filters on a specific field, apply each filter in turn
            node = self
            for operator, value in kwargs.items():
                node = node.filter(*args, **{operator: value})
            return node

        operator, value = list(kwargs.items())[0]
        if operator == "between":
            # convert a between filter into its two components
            return self.filter(*args, on_or_after=value[0], on_or_before=value[1])

        assert len(args) == len(kwargs) == 1

        operator = _OPERATOR_MAPPING[operator]
        return FilteredTable(
            source=self, column=args[0], operator=operator, value=value
        )

    def earliest(self, *columns):
        columns = columns or ("date",)
        return self.first_by(*columns)

    def latest(self, *columns):
        columns = columns or ("date",)
        return self.last_by(*columns)

    def first_by(self, *columns):
        assert columns
        return Row(source=self, sort_columns=columns, descending=False)

    def last_by(self, *columns):
        assert columns
        return Row(source=self, sort_columns=columns, descending=True)

    def date_in_range(self, date, start_column="date_start", end_column="date_end"):
        """
        A filter that returns the latest of two boundary date fields, where start values
        are <= a target date and end values are >= a target. If more than one entry matches,
        the latest one will be returned.
        Note that this filter currently expects that a value will be present for BOTH
        start and end columns.
        """
        return (
            self.filter(start_column, less_than_or_equals=date)
            .filter(end_column, greater_than_or_equals=date)
            .last_by(start_column, end_column)
        )

    def exists(self, column="patient_id"):
        return self.aggregate("exists", column)

    def count(self, column):
        return self.aggregate("count", column)

    def sum(self, column):  # noqa: A003
        return self.aggregate("sum", column)

    def aggregate(self, function, column):
        return ValueFromAggregate(self, function, column)


class FilteredTable(Table):
    def __init__(self, source, column, operator, value):
        self.source = source
        self.column = column
        self.operator = operator
        self.value = value


class Column(QueryNode):
    def __init__(self, source, column):
        self.source = source
        self.column = column


class Row(QueryNode):
    def __init__(self, source, sort_columns, descending=False):
        self.source = source
        self.sort_columns = sort_columns
        self.descending = descending

    def get(self, column):
        return ValueFromRow(source=self, column=column)


class Value(QueryNode):
    ...


class ValueFromRow(Value):
    def __init__(self, source, column):
        self.source = source
        self.column = column


class ValueFromAggregate(Value):
    def __init__(self, source, function, column):
        self.source = source
        self.function = function
        self.column = column


def categorise(mapping, default):
    return Category(mapping, default)


CategoryGroup = namedtuple("CategoryGroup", ("source", "operator", "value"))


class Category(QueryNode):
    def __init__(self, groups, default):
        self.default = default
        self.definitions = groups
