import dataclasses
import datetime
from enum import Enum
from functools import singledispatch
from typing import Union

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
    "DomainMismatchError",
]


#
# UTILITY CLASSES
#

# Static value types
Value = Union[None, bool, int, float, str, datetime.datetime, datetime.date]


class Position(Enum):
    FIRST = "first"
    LAST = "last"

    def __repr__(self):
        # Gives us `self == eval(repr(self))` as for dataclasses
        return f"{self.__class__.__name__}.{self.name}"


@dataclasses.dataclass(frozen=True)
class Codelist:
    codes: tuple
    system: str
    has_categories: bool = False

    def __post_init__(self):
        if self.has_categories:
            raise NotImplementedError("Categorised codelists are currently unsupported")

    def __repr__(self):
        if len(self.codes) > 5:
            codes = self.codes[:5] + ("...",)
        else:
            codes = self.codes
        return f"Codelist(system={self.system}, codes={codes})"


# BASIC TYPES
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
    ...


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


class SelectTable(ManyRowsPerPatientFrame):
    name: str


class SelectPatientTable(OneRowPerPatientFrame):
    name: str


class SelectColumn(Series):
    name: str
    source: Frame


class Filter(ManyRowsPerPatientFrame):
    source: ManyRowsPerPatientFrame
    condition: Series


class Sort(SortedFrame):
    source: ManyRowsPerPatientFrame
    sort_by: Series


class PickOneRowPerPatient(OneRowPerPatientFrame):
    position: Position
    source: SortedFrame


# An aggregation is any operation which accepts many-rows-per-patient series and
# returns a one-row-per-patient series. The below is a base class which we use to remove
# duplication in our aggregation definitions as they currently all accept just a single
# series. But an aggregation does not need to subclass this, just so long as it has the
# right signature.
class Aggregation(OneRowPerPatientSeries):
    source: Series


# All available aggregations (using a class as a namespace)
class AggregateByPatient:
    class Exists(Aggregation):
        ...

    class Min(Aggregation):
        ...

    class Max(Aggregation):
        ...

    class Count(Aggregation):
        ...

    class Sum(Aggregation):
        ...

    # This is unusual aggregation in that while it collapses multiple values per patient
    # down to a single value per patient (as all aggregations must) the value it
    # produces is a set-like object containing all of its input values. This enables
    # them to be used as arguments to the In/NotIn fuctions which require something
    # set-like as their RHS argument.
    class CombineAsSet(Aggregation):
        ...


# A function is any operation which takes series and values and returns a series. The
# dimension of the series it returns will be the highest dimension of its inputs i.e. if
# any of its inputs has many-rows-per-patient then its output will too. The below base
# classs are used to remove duplication in our function definitions. But a function does
# not need to subclass one of these, just so long as it has the right signature.
class UnaryFunction(Series):
    source: Series


class BinaryFunction(Series):
    lhs: Union[Series, Value]
    rhs: Union[Series, Value]


# All available functions (using a class as a namespace)
class Function:

    # Comparison
    class EQ(BinaryFunction):
        ...

    class NE(BinaryFunction):
        ...

    class LT(BinaryFunction):
        ...

    class LE(BinaryFunction):
        ...

    class GT(BinaryFunction):
        ...

    class GE(BinaryFunction):
        ...

    # Boolean
    class And(BinaryFunction):
        ...

    class Or(BinaryFunction):
        ...

    class Not(UnaryFunction):
        ...

    # Null handling
    class IsNull(UnaryFunction):
        ...

    # Arithmetic
    class Add(BinaryFunction):
        ...

    class Subtract(BinaryFunction):
        ...

    # Dates
    class RoundToFirstOfMonth(UnaryFunction):
        ...

    class RoundToFirstOfYear(UnaryFunction):
        ...

    class DateAdd(BinaryFunction):
        ...

    class DateSubtract(BinaryFunction):
        ...

    class DateDifference(Series):
        start: Union[Series, datetime.date]
        end: Union[Series, datetime.date]
        units: str

    # Containment is a special case: its right-hand side must be something vector-like i.e.
    # something containing multiple values. To build a series whose values are vectors,
    # use the `CombineAsSet` aggregation.
    class In(Series):
        lhs: Series
        rhs: Union[Series, tuple[Value], Codelist]

    class NotIn(In):
        ...


class Categorise(Series):
    categories: dict[Value, Series]
    default: Value

    def __hash__(self):
        # `categories` is a dict and so not hashable by default, but we treat it as
        # immutable once created so we're fine to make it hashable
        return hash((tuple(self.categories.items()), self.default))


# We don't currently support this in the DSL or the Query Engine but we include it for
# completeness
class Join(ManyRowsPerPatientFrame):
    lhs: Frame
    rhs: Frame


# VALIDATION
#
# The main thing we need to validate here is the "domain constraint". Frames and series
# which are in one-row-per-patient form can be combined arbitrarily because we can JOIN
# using the patient_id and be sure that we're not creating new rows. But for operations
# involving many-rows-per-patient inputs we need to ensure that they are all drawn from
# the same underlying table. (We call this the "domain" for set theoretic reasons which
# the margin of this comment are too small to contain.)

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

    # The one exception to the "common domain" rule is the Join operation which takes
    # frames from two different domains and produces a new domain
    if not isinstance(node, Join):
        validate_children_have_common_domain(node)


def validate_children_have_common_domain(node):
    domains = get_domains(node)
    non_patient_domains = domains - {PATIENT_DOMAIN}
    if len(non_patient_domains) > 1:
        raise DomainMismatchError(
            f"Attempt to combine multiple domains:\n{non_patient_domains}"
            f"\nIn node:\n{node}"
        )


# For most operations, their domain is the just the domains of all their children.
@singledispatch
def get_domains(node):
    return set().union(
        *[get_domains(child_node) for child_node in get_child_nodes(node)]
    )


# But these operations create new domains.
@get_domains.register(SelectTable)
@get_domains.register(Join)
def get_domain_roots(node):
    return {node}


# And these operations are guaranteed to produce output in the patient domain.
@get_domains.register(OneRowPerPatientFrame)
@get_domains.register(OneRowPerPatientSeries)
def get_domains_for_one_row_per_patient_operations(node):
    return {PATIENT_DOMAIN}


# Quick and lazy way of getting child nodes using dataclass introspection
@singledispatch
def get_child_nodes(node):
    return [
        value
        for value in [getattr(node, field.name) for field in dataclasses.fields(node)]
        if isinstance(value, Node)
    ]


# The above bit of dynamic cheekiness doesn't work for Categorise whose children are
# nested inside a dict object
@get_child_nodes.register(Categorise)
def get_child_nodes_for_categorise(node):
    return node.categories.values()
