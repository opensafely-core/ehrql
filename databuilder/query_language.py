from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


class ValidationError(Exception):
    ...


def table(name):
    return Table(name)


# A note about dataclasses...  We will need to store instances of the classes in this
# module in sets, which requires them to be hashable.  As such, we require instances to
# be frozen.  This means we cannot mutate the fields of an instance once it has been
# created.  Additionally, in order for the comparison operators on Value and its
# subclasses to work, we need to stop dataclasses from overriding these methods on the
# subclasses.


class QueryNode:
    def _get_referenced_nodes(self):
        """
        Return a tuple of all QueryNodes to which this node holds a reference
        """
        raise NotImplementedError()


@dataclass(frozen=True)
class Comparator(QueryNode):
    """A generic comparator to represent a comparison between a source object and a
    value.

    The simplest comparator is created from an expression such as `foo > 3` and will
    have a lhs ('foo'; a Value object), operator ('__gt__') and a rhs (3; a simple type
    - str/int/float/None).  The lhs and rhs of a Comparator can themselves be
    Comparators, which are to be connected with self.connector.
    """

    connector: Any = None
    negated: bool = False
    lhs: Any = None
    operator: Any = None
    rhs: Any = None

    def _get_referenced_nodes(self):
        nodes = ()
        if isinstance(self.lhs, QueryNode):
            nodes += (self.lhs,)
        if isinstance(self.rhs, QueryNode):
            nodes += (self.rhs,)
        return nodes

    def __and__(self, other):
        return self._combine(other, "and_")

    def __or__(self, other):
        return self._combine(other, "or_")

    def __invert__(self):
        return type(self)(
            connector=self.connector,
            negated=not self.negated,
            lhs=self.lhs,
            operator=self.operator,
            rhs=self.rhs,
        )

    @staticmethod
    def _raise_comparison_error():
        raise RuntimeError(
            "Invalid operation; cannot perform logical operations on a Comparator"
        )

    def __gt__(self, other):
        self._raise_comparison_error()

    def __ge__(self, other):
        self._raise_comparison_error()

    def __lt__(self, other):
        self._raise_comparison_error()

    def __le__(self, other):
        self._raise_comparison_error()

    def __eq__(self, other):
        return self._compare(other, "__eq__")

    def __ne__(self, other):
        return self._compare(other, "__ne__")

    def _combine(self, other, conn):
        assert isinstance(other, Comparator)
        return type(self)(connector=conn, lhs=self, rhs=other)

    def _compare(self, other, operator):
        return type(self)(operator=operator, lhs=self, rhs=other)


def boolean_comparator(obj, negated=False):
    """returns a comparator which represents a comparison against null values"""
    return Comparator(lhs=obj, operator="__ne__", rhs=None, negated=negated)


class BaseTable(QueryNode):
    def get(self, column):
        return Column(source=self, column=column)

    def filter(self, *args: str, **kwargs: Any) -> BaseTable:  # noqa: A003
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
        include_null = kwargs.pop("include_null", False)
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

        if operator in ("equals", "not_equals") and isinstance(
            value, (Codelist, Column)
        ):
            raise TypeError(
                f"You can only use '{operator}' to filter a column by a single value.\n"
                f"To filter using a {value.__class__.__name__}, use 'is_in/not_in'."
            )

        if operator == "is_in" and not isinstance(value, (Codelist, Column)):
            # convert non-codelist in values to tuple
            value = tuple(value)
        assert len(args) == len(kwargs) == 1

        operator = _OPERATOR_MAPPING[operator]
        return FilteredTable(
            source=self,
            column=args[0],
            operator=operator,
            value=value,
            or_null=include_null,
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

    def date_in_range(
        self, date, start_column="date_start", end_column="date_end", include_null=True
    ):
        """
        A filter that returns rows for which a date falls between a start and end date (inclusive).
        Null end date values are included by default
        """
        return self.filter(start_column, less_than_or_equals=date).filter(
            end_column, greater_than_or_equals=date, include_null=include_null
        )

    def exists(self, column="patient_id"):
        return self.aggregate("exists", column)

    def count(self, column="patient_id"):
        return self.aggregate("count", column)

    def sum(self, column):  # noqa: A003
        return self.aggregate("sum", column)

    def aggregate(self, function, column):
        output_column = f"{column}_{function}"
        row = RowFromAggregate(self, function, column, output_column)
        return ValueFromAggregate(row, output_column)


@dataclass(frozen=True)
class Table(BaseTable):
    name: str

    def _get_referenced_nodes(self):
        # Table nodes are always root nodes in the query DAG and don't reference other
        # nodes
        return ()

    def imd_rounded_as_of(self, reference_date):
        """
        A convenience method to retrieve the IMD on the reference date.
        """
        if self.name != "patient_address":
            raise NotImplementedError(
                "This method is only available on the patient_address table"
            )

        # Note that current addresses are recorded with an EndDate of
        # 9999-12-31 (TPP) or Null (Graphnet). Where address periods overlap we use the one with the
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


# @dataclass(unsafe_hash=True)
@dataclass(frozen=True)
class FilteredTable(BaseTable):
    source: Any
    column: Any
    operator: Any
    value: Any
    or_null: bool = False

    def _get_referenced_nodes(self):
        nodes = (self.source,)
        if isinstance(self.value, QueryNode):
            nodes += (self.value,)
        return nodes


@dataclass(frozen=True)
class Column(QueryNode):
    source: Any
    column: Any

    def _get_referenced_nodes(self):
        return (self.source,)


@dataclass(frozen=True)
class Row(QueryNode):
    source: Any
    sort_columns: Any
    descending: Any

    def _get_referenced_nodes(self):
        return (self.source,)

    def get(self, column):
        return ValueFromRow(source=self, column=column)


@dataclass(frozen=True)
class RowFromAggregate(QueryNode):
    source: QueryNode
    function: Any
    input_column: Any
    output_column: Any

    def _get_referenced_nodes(self):
        return (self.source,)


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


@dataclass(frozen=True, eq=False, order=False)
class ValueFromRow(Value):
    source: Any
    column: Any

    def _get_referenced_nodes(self):
        return (self.source,)


@dataclass(frozen=True, eq=False, order=False)
class ValueFromAggregate(Value):
    source: RowFromAggregate
    column: Any

    def _get_referenced_nodes(self):
        return (self.source,)


def categorise(mapping, default=None):
    mapping = {
        key: boolean_comparator(value) if isinstance(value, Value) else value
        for key, value in mapping.items()
    }
    return ValueFromCategory(mapping, default)


@dataclass(frozen=True, eq=False, order=False)
class ValueFromCategory(Value):
    definitions: dict
    default: str | int | float | None

    def _get_referenced_nodes(self):
        nodes = ()
        for value in self.definitions.values():
            assert isinstance(value, QueryNode)
            nodes += (value,)
        return nodes


@dataclass(frozen=True)
class Codelist(QueryNode):
    codes: tuple
    system: str
    has_categories: bool = False

    def _get_referenced_nodes(self):
        return ()

    def __post_init__(self):
        if self.has_categories:
            raise NotImplementedError("Categorised codelists are currently unsupported")

    def __repr__(self):
        if len(self.codes) > 5:
            codes = self.codes[:5] + ("...",)
        else:
            codes = self.codes
        return f"Codelist(system={self.system}, codes={codes})"


class ValueFromFunction(Value):
    def __init__(self, *args):
        self.arguments = args

    def _get_referenced_nodes(self):
        return tuple(arg for arg in self.arguments if isinstance(arg, QueryNode))


class DateDifferenceInYears(ValueFromFunction):
    pass


class RoundToFirstOfMonth(ValueFromFunction):
    pass


class RoundToFirstOfYear(ValueFromFunction):
    pass
