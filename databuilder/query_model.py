import dataclasses
from collections.abc import Mapping, Set
from datetime import date
from enum import Enum
from functools import singledispatch
from typing import Any, Optional, TypeVar

# mypy: ignore-errors


# The below classes are the public API surface of the query model
__all__ = [
    "SelectTable",
    "SelectPatientTable",
    "SelectColumn",
    "Filter",
    "Sort",
    "PickOneRowPerPatient",
    "Position",
    "AggregateByPatient",
    "Function",
    "Categorise",
    "TableSchema",
    "Code",
    "DomainMismatchError",
]


#
# VALUE TYPES
#


# TypeVars so we can enforce that e.g. comparison functions take two values of the same
# type without specifying what that type has to be
T = TypeVar("T")
Numeric = TypeVar("Numeric", int, float)


@dataclasses.dataclass(frozen=True)
class Code:
    "A code is a string tagged with the coding system it's drawn from"
    value: str
    system: str


class Position(Enum):
    FIRST = "first"
    LAST = "last"

    def __repr__(self):
        # Gives us `self == eval(repr(self))` as for dataclasses
        return f"{self.__class__.__name__}.{self.name}"


class TableSchema:
    "Defines a mapping of column names to types"

    def __init__(self, name, **columns):
        # `name` can be arbitrary here, but supplying a bound name for the schema in
        # local scope will give a correctly executable repr
        self.name = name
        self.columns = columns

    def __getitem__(self, column):  # pragma: no cover
        return self.columns[column]

    def __repr__(self):
        return self.name


# BASIC QUERY MODEL TYPES
#
# The Query Model consists of operations on "frames" and "series". A frame is a table-like
# thing that has rows and columns, and a series is a column-like thing that contains a
# sequence of values. Frames can be created from SQL tables, and then various filtering,
# transformation and sorting operations can be applied to produce new frames. Likewise,
# a series can be created from a SQL column and then transformed and combined with
# others to produce new series.
#
# Central to the Query Model design is that these frames and series have an additional
# property called their "dimension": do they contain at most one row per patient, or
# might they contain many rows?


class Node:
    "Abstract base class for all objects in the Query Model"

    def __init_subclass__(cls, **kwargs):
        # All nodes in the query model are frozen dataclasses
        dataclasses.dataclass(cls, frozen=True)

    def __post_init__(self):
        # validate the things which have to be checked dynamically
        validate_node(self)


class Frame(Node):
    ...


class Series(Node):
    def __class_getitem__(cls, type_):
        # Series have an "inner" type denoting the type of value they contain e.g
        # `Series[int]`. This is the method which makes that syntax work. At the moment
        # we don't do anything with this type, we just return the original class
        # unmodified. Later we will handle this properly and validate the types.
        return cls


class OneRowPerPatientFrame(Frame):
    ...


class ManyRowsPerPatientFrame(Frame):
    ...


class OneRowPerPatientSeries(Series):
    ...


class ManyRowsPerPatientSeries(Series):
    ...


class SortedFrame(ManyRowsPerPatientFrame):
    ...


# OPERATIONS
#
# Operations indicate the kind of thing they return by subclassing one of the basic
# types above.


# `Value` wraps a single static value in a one-row-per-patient series which just has
# that value for every patient. This simplifies the signature of all other operations
# which no longer need to care about static values.
class Value(OneRowPerPatientSeries[T]):
    value: T


class SelectTable(ManyRowsPerPatientFrame):
    name: str
    # A schema is a mapping from available colum names to types which allows us to check
    # that operations only use columns which actually exist and are of the correct type.
    # It's optional because we don't *need* it to construct a query, but we're obviously
    # more limited in the validation we can do without it.
    schema: Optional[TableSchema] = None


class SelectPatientTable(OneRowPerPatientFrame):
    name: str
    schema: Optional[TableSchema] = None


class SelectColumn(Series):
    source: Frame
    name: str


class Filter(ManyRowsPerPatientFrame):
    source: ManyRowsPerPatientFrame
    condition: Series[bool]


class Sort(SortedFrame):
    source: ManyRowsPerPatientFrame
    sort_by: Series[Any]


class PickOneRowPerPatient(OneRowPerPatientFrame):
    source: SortedFrame
    position: Position


# An aggregation is any operation which accepts many-rows-per-patient series and returns
# a one-row-per-patient series. Below are all available aggregations (using a class as a
# namespace).
class AggregateByPatient:
    class Exists(OneRowPerPatientSeries[bool]):
        source: Series[Any]

    class Min(OneRowPerPatientSeries[T]):
        source: Series[T]

    class Max(OneRowPerPatientSeries[T]):
        source: Series[T]

    class Count(OneRowPerPatientSeries[int]):
        source: Series[Any]

    class Sum(OneRowPerPatientSeries[Numeric]):
        source: Series[Numeric]

    # This is an unusual aggregation in that while it collapses multiple values per patient
    # down to a single value per patient (as all aggregations must) the value it
    # produces is a set-like object containing all of its input values. This enables
    # them to be used as arguments to the In/NotIn fuctions which require something
    # set-like as their RHS argument.
    class CombineAsSet(OneRowPerPatientSeries[Set[T]]):
        source: Series[T]


# Remove some duplication from the definition of the comparison functions
class ComparisonFunction(Series[bool]):
    lhs: Series[T]
    rhs: Series[T]


# A function is any operation which takes series and values and returns a series. The
# dimension of the series it returns will be the highest dimension of its inputs i.e. if
# any of its inputs has many-rows-per-patient then its output will too.  Below are all
# available functions (using a class as a namespace).
class Function:

    # Comparison
    class EQ(ComparisonFunction):
        ...

    class NE(ComparisonFunction):
        ...

    class LT(ComparisonFunction):
        ...

    class LE(ComparisonFunction):
        ...

    class GT(ComparisonFunction):
        ...

    class GE(ComparisonFunction):
        ...

    # Boolean
    class And(Series[bool]):
        lhs: Series[bool]
        rhs: Series[bool]

    class Or(Series[bool]):
        lhs: Series[bool]
        rhs: Series[bool]

    class Not(Series[bool]):
        source: Series[bool]

    # Null handling
    class IsNull(Series[bool]):
        source: Series[Any]

    # Arithmetic
    class Add(Series[Numeric]):
        lhs: Series[Numeric]
        rhs: Series[Numeric]

    class Subtract(Series[Numeric]):
        lhs: Series[Numeric]
        rhs: Series[Numeric]

    # Dates
    # TODO: Our date handling needs thinking through. Possibly we need an explicit
    # datedelta type. Consider the below functions provisional.
    class RoundToFirstOfMonth(Series[date]):
        source: Series[date]

    class RoundToFirstOfYear(Series[date]):
        source: Series[date]

    class DateAdd(Series[date]):
        lhs: Series[date]
        rhs: Series[int]

    class DateSubtract(Series[date]):
        lhs: Series[date]
        rhs: Series[int]

    class DateDifference(Series[int]):
        start: Series[date]
        end: Series[date]
        units: Series[str]

    class YearFromDate(Series[int]):
        source: Series[date]

    # Containment is a special case: its right-hand side must be something vector-like i.e.
    # something containing multiple values. To build a series whose values are vectors,
    # use the `CombineAsSet` aggregation.
    class In(Series[bool]):
        lhs: Series[T]
        rhs: Series[Set[T]]


class Categorise(Series[T]):
    categories: Mapping[Series[T], Series[bool]]
    default: Series[T]

    def __hash__(self):
        # `categories` is a dict and so not hashable by default, but we treat it as
        # immutable once created so we're fine to make it hashable
        return hash((tuple(self.categories.items()), self.default))


# TODO: We don't currently support Join in the DSL or the Query Engine but this is the
# signature it will have when we do. Also note that the Join operation is the one
# exception to the "common domain constraint" explained below as it's the one operation
# which is explicitly designed to take inputs from two different domains and produce a
# single, new domain as output.
#
# class Join(ManyRowsPerPatientFrame):
#     lhs: Frame
#     rhs: Frame


# VALIDATION
#

PATIENT_DOMAIN = object()


class DomainMismatchError(Exception):
    ...


def validate_node(node):
    # TODO: Runtime type validation (i.e. only acceptable types are passed in), possibly
    # using something like pydantic.

    # TODO: Validation of the "inner" types i.e. a series may contain date values and we
    # want to make it an error if you try to compare these to an int. And there are
    # several places (e.g. a Filter condition) where we require suppied series to have
    # boolean type. We'll need the DSL to get these types from the schema and pass them
    # in somehow.

    # The main thing we need to validate here is the "domain constraint". Frames and series
    # which are in one-row-per-patient form can be combined arbitrarily because we can JOIN
    # using the patient_id and be sure that we're not creating new rows. But for operations
    # involving many-rows-per-patient inputs we need to ensure that they are all drawn from
    # the same underlying table. (We call this the "domain" for set theoretic reasons which
    # the margin of this comment are too small to contain.) Note that when we add a Join
    # operation that will be the one explicit exception to this rule.
    validate_inputs_have_common_domain(node)


def validate_inputs_have_common_domain(node):
    domains = get_domains(node)
    non_patient_domains = domains - {PATIENT_DOMAIN}
    if len(non_patient_domains) > 1:
        raise DomainMismatchError(
            f"Attempt to combine multiple domains:\n{non_patient_domains}"
            f"\nIn node:\n{node}"
        )


# For most operations, their domain is the just the domains of all their inputs
@singledispatch
def get_domains(node):
    return set().union(
        *[get_domains(input_node) for input_node in get_input_nodes(node)]
    )


# But these operations create new domains
@get_domains.register(SelectTable)
def get_domain_roots(node):
    return {node}


# And these operations are guaranteed to produce output in the patient domain
@get_domains.register(OneRowPerPatientFrame)
@get_domains.register(OneRowPerPatientSeries)
def get_domains_for_one_row_per_patient_operations(node):
    return {PATIENT_DOMAIN}


# Quick and lazy way of getting input nodes using dataclass introspection
@singledispatch
def get_input_nodes(node):
    return [
        value
        for value in [getattr(node, field.name) for field in dataclasses.fields(node)]
        if isinstance(value, Node)
    ]


# The above bit of dynamic cheekiness doesn't work for Categorise whose inputs are
# nested inside a dict object
@get_input_nodes.register(Categorise)
def get_input_nodes_for_categorise(node):
    return [*node.categories.keys(), *node.categories.values(), node.default]
