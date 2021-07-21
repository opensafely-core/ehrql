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


class Comparator:
    """A generic comparator to represent a comparison between a source object and a value"""

    def __init__(
        self,
        connector=None,
        negated=False,
        lhs=None,
        operator=None,
        rhs=None,
    ):
        """
        Construct a new Comparator.
        The simplest comparator is created from an expression such as `foo > 3` and
        will have a lhs ('foo'; a Value object), operator ('__gt__')
        and a rhs (3; a simple type - str/int/float/None).
        The lhs and rhs of a Comparator can themselves be Comparators, which are to be
        connected with self.connector.
        """
        self.connector = connector
        self.negated = negated
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs

    def __repr__(self):
        return f"Comparator(connector={self.connector}, negated={self.negated}, lhs={self.lhs}, operator={self.operator}, rhs={self.rhs})"

    def __and__(self, other):
        return self._combine(other, "and_")

    def __or__(self, other):
        return self._combine(other, "or_")

    def __invert__(self):
        obj = self.copy()
        obj.negated = not self.negated
        return obj

    def copy(self):
        obj = type(self)(
            connector=self.connector,
            negated=self.negated,
            lhs=self.lhs,
            operator=self.operator,
            rhs=self.rhs,
        )
        return obj

    def _combine(self, other, conn):
        if not (isinstance(other, Comparator)):
            raise TypeError(other)
        obj = type(self)()
        obj.connector = conn
        obj.lhs = self
        obj.rhs = other
        return obj


def boolean_comparator(obj, negated=False):
    """returns a comparator which represents a comparison against null values"""
    return Comparator(lhs=obj, operator="__ne__", rhs=None, negated=negated)


class QueryNode:
    pass


class Table(QueryNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Table(name={self.name})"

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
        A filter that returns rows for which a date falls between a start and end date (inclusive).
        Note that this filter currently expects that a value will be present for BOTH
        start and end columns.
        """
        return self.filter(start_column, less_than_or_equals=date).filter(
            end_column, greater_than_or_equals=date
        )

    def exists(self, column="patient_id"):
        return self.aggregate("exists", column)

    def count(self, column):
        return self.aggregate("count", column)

    def sum(self, column):  # noqa: A003
        return self.aggregate("sum", column)

    def aggregate(self, function, column):
        return ValueFromAggregate(self, function, column)

    def imd_rounded_as_of(self, reference_date):
        """
        A convenience method to retrieve the IMD on the reference date.
        """
        if self.name != "patient_address":
            raise NotImplementedError(
                "This method is only available on the patient_address table"
            )

        # Note that current addresses are recorded with an EndDate of
        # 9999-12-31. Where address periods overlap we use the one with the
        # most recent start date. If there are several with the same start date
        # we use the longest one (i.e. with the latest end date). We then
        # prefer addresses which have a postcode and inally we use the address ID as a
        # tie-breaker.
        return (
            self.date_in_range(reference_date)
            .last_by("date_start", "date_end", "has_postcode", "patientaddress_id")
            .get("index_of_multiple_deprivation_rounded")
        )

    def age_as_of(self, reference_date):
        if self.name != "patients":
            raise NotImplementedError(
                "This method is only available on the patients table"
            )
        return DateDifferenceInYears(
            self.first_by("patient_id").get("date_of_birth"), reference_date
        )


class FilteredTable(Table):
    def __init__(self, source, column, operator, value):
        self.source = source
        self.column = column
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"FilteredTable(source={self.source}, column={self.column}, operator={self.operator}, value={self.value})"


class Column(QueryNode):
    def __init__(self, source, column):
        self.source = source
        self.column = column

    def __repr__(self):
        return f"Column(source={self.source}, column={self.column})"


class Row(QueryNode):
    def __init__(self, source, sort_columns, descending=False):
        self.source = source
        self.sort_columns = sort_columns
        self.descending = descending

    def __repr__(self):
        return f"Row(source={self.source}, columns={self.sort_columns}, descending={self.descending})"

    def get(self, column):
        return ValueFromRow(source=self, column=column)


class Value(QueryNode):
    @staticmethod
    def _other_as_comparator(other):
        if isinstance(other, Value):
            other = boolean_comparator(other)
        return other

    def _get_comparator(self, operator, other):
        other = self._other_as_comparator(other)
        return Comparator(lhs=self, operator=operator, rhs=other)

    def __gt__(self, other):
        return self._get_comparator("__gt__", other)

    def __ge__(self, other):
        return self._get_comparator("__ge__", other)

    def __lt__(self, other):
        return self._get_comparator("__lt__", other)

    def __le__(self, other):
        return self._get_comparator("__le__", other)

    def __eq__(self, other):
        return self._get_comparator("__eq__", other)

    def __ne__(self, other):
        return self._get_comparator("__ne__", other)

    def __and__(self, other):
        other = self._other_as_comparator(other)
        return boolean_comparator(self) & other

    def __or__(self, other):
        other = self._other_as_comparator(other)
        return boolean_comparator(self) | other

    def __invert__(self):
        return boolean_comparator(self, negated=True)

    def __hash__(self):
        return id(self)


class ValueFromRow(Value):
    def __init__(self, source, column):
        self.source = source
        self.column = column

    def __repr__(self):
        return f"ValueFromRow(source={self.source}, column={self.column})"


class ValueFromAggregate(Value):
    def __init__(self, source, function, column):
        self.source = source
        self.function = function
        self.column = column

    def __repr__(self):
        return f"ValueFromAggregate(source={self.source}, function={self.function}, column={self.column})"


def categorise(mapping, default):
    mapping = {
        key: boolean_comparator(value) if isinstance(value, Value) else value
        for key, value in mapping.items()
    }
    return ValueFromCategory(mapping, default)


class ValueFromCategory(Value):
    def __init__(self, definitions, default):
        self.default = default
        self.definitions = definitions

    def __repr__(self):
        return (
            f"ValueFromCategory(default={self.default}, definitions={self.definitions})"
        )


class Codelist(QueryNode):
    def __init__(self, codes, system, has_categories=False):
        if has_categories:
            raise NotImplementedError("Categorised codelists are currently unsupported")
        self.codes = list(codes)
        self.system = system

    def __repr__(self):
        if len(self.codes) > 5:
            codes = self.codes[:5] + ["..."]
        else:
            codes = self.codes
        return f"Codelist(system={self.system}, codes={codes})"


class ValueFromFunction(Value):
    def __init__(self, *args):
        self.arguments = args

    def __repr__(self):
        return f"{self.__class__.__name__}(arguments={self.arguments})"


class DateDifferenceInYears(ValueFromFunction):
    pass
