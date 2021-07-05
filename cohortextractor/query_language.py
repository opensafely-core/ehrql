def table(name):
    return Table(name)


class QueryNode:
    pass


class Table(QueryNode):
    def __init__(self, name):
        self.name = name

    def get(self, column):
        return Column(source=self, column=column)

    @property
    def _filter_operator_mapping(self):
        return {
            "equals": "__eq__",
            "less_than": "__lt__",
            "less_than_or_equals": "__le__",
            "greater_than": "__gt__",
            "greater_than_or_equals": "__ge__",
            "on_or_before": "__le__",
            "on_or_after": "__ge__",
        }

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

        operator = self._filter_operator_mapping[operator]
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

    def exists(self):
        return self.aggregate("exists", "patient_id")

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
