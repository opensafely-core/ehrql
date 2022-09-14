import dataclasses
import datetime

from databuilder import query_model as qm
from databuilder.codes import BaseCode, Codelist
from databuilder.population_validation import validate_population_definition
from databuilder.query_model import get_series_type, has_one_row_per_patient

# This gets populated by the `__init_subclass__` methods of EventSeries and
# PatientSeries. Its structure is:
#
#   (<type>, <is_patient_level>): <SeriesClass>
#
# For example:
#
#   (bool, False): BoolEventSeries,
#   (bool, True): BoolPatientSeries,
#
REGISTERED_TYPES = {}


# Because ehrQL classes override `__eq__` we can't use them as dictionary keys. So where
# the query model expects dicts we represent them as lists of pairs, which the
# `_apply()` function can convert to dicts when it passes them to the query model.
class _DictArg(list):
    "Internal class for passing around dictionary arguments"


class Dataset:
    def set_population(self, population):
        validate_population_definition(population.qm_node)
        object.__setattr__(self, "population", population)

    def __setattr__(self, name, value):
        if name == "population":
            raise AttributeError(
                "Cannot set column 'population'; use set_population() instead"
            )
        if getattr(self, name, None):
            raise AttributeError(f"'{name}' is already set and cannot be reassigned")
        if not qm.has_one_row_per_patient(value.qm_node):
            raise TypeError(
                f"Invalid column '{name}'. Dataset columns must return one row per patient"
            )
        super().__setattr__(name, value)


def compile(dataset):  # noqa A003
    return {k: v.qm_node for k, v in vars(dataset).items() if isinstance(v, BaseSeries)}


# BASIC SERIES TYPES
#


@dataclasses.dataclass(frozen=True)
class BaseSeries:
    qm_node: qm.Node

    def __hash__(self):
        # The issue here is not mutability but the fact that we overload `__eq__` for
        # syntatic sugar, which makes these types spectacularly ill-behaved as dict keys
        raise TypeError(f"unhashable type: {self.__class__.__name__!r}")

    # These are the basic operations that apply to any series regardless of type or
    # dimension
    def __eq__(self, other):
        return _apply(qm.Function.EQ, self, other)

    def __ne__(self, other):
        return _apply(qm.Function.NE, self, other)

    def is_null(self):
        return _apply(qm.Function.IsNull, self)

    def is_not_null(self):
        return self.is_null().__invert__()

    def is_in(self, other):
        # The query model requires an immutable Set type for containment queries, but
        # that's a bit user-unfriendly so we accept other types here and convert them
        if isinstance(other, (tuple, list, set)):
            other = frozenset(other)
        return _apply(qm.Function.In, self, other)

    def is_not_in(self, other):
        return self.is_in(other).__invert__()

    def map_values(self, mapping):
        """
        Accepts a dictionary mapping one set of values to another and applies that
        mapping to the series
        """
        cases = _DictArg(
            (self == from_value, to_value) for from_value, to_value in mapping.items()
        )
        return _apply(qm.Case, cases)

    def if_null_then(self, other):
        return case(
            when(self.is_not_null()).then(self),
            default=other,
        )


class EventSeries(BaseSeries):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the series using its `_type` attribute
        REGISTERED_TYPES[cls._type, False] = cls

    # If we end up with any type-agnostic aggregations (count non-null, maybe?) then
    # they would be defined here as well


class PatientSeries(BaseSeries):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the series using its `_type` attribute
        REGISTERED_TYPES[cls._type, True] = cls


# BOOLEAN SERIES
#


class BoolFunctions:
    def __invert__(self):
        return _apply(qm.Function.Not, self)

    def __and__(self, other):
        return _apply(qm.Function.And, self, other)

    def __or__(self, other):
        return _apply(qm.Function.Or, self, other)


class BoolEventSeries(BoolFunctions, EventSeries):
    _type = bool


class BoolPatientSeries(BoolFunctions, PatientSeries):
    _type = bool


# METHODS COMMON TO ALL COMPARABLE TYPES
#


class ComparableFunctions:
    def __lt__(self, other):
        return _apply(qm.Function.LT, self, other)

    def __le__(self, other):
        return _apply(qm.Function.LE, self, other)

    def __ge__(self, other):
        return _apply(qm.Function.GE, self, other)

    def __gt__(self, other):
        return _apply(qm.Function.GT, self, other)


class ComparableAggregations:
    def minimum_for_patient(self):
        return _apply(qm.AggregateByPatient.Min, self)

    def maximum_for_patient(self):
        return _apply(qm.AggregateByPatient.Max, self)


# STRING SERIES
#


class StrFunctions(ComparableFunctions):
    def contains(self, other):
        return _apply(qm.Function.StringContains, self, other)


class StrAggregations(ComparableAggregations):
    "Empty for now"


class StrEventSeries(StrFunctions, StrAggregations, EventSeries):
    _type = str


class StrPatientSeries(StrFunctions, PatientSeries):
    _type = str


# NUMERIC SERIES
#


class NumericFunctions(ComparableFunctions):
    def __neg__(self):
        return _apply(qm.Function.Negate, self)

    def __add__(self, other):
        return _apply(qm.Function.Add, self, other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return _apply(qm.Function.Subtract, self, other)

    def __rsub__(self, other):
        return other + -self

    def as_int(self):
        return _apply(qm.Function.CastToInt, self)

    def as_float(self):
        return _apply(qm.Function.CastToFloat, self)


class NumericAggregations(ComparableAggregations):
    def sum_for_patient(self):
        return _apply(qm.AggregateByPatient.Sum, self)


class IntEventSeries(NumericFunctions, NumericAggregations, EventSeries):
    _type = int


class IntPatientSeries(NumericFunctions, PatientSeries):
    _type = int


class FloatEventSeries(NumericFunctions, NumericAggregations, EventSeries):
    _type = float


class FloatPatientSeries(NumericFunctions, PatientSeries):
    _type = float


# DATE SERIES
#


def parse_date_if_str(value):
    if isinstance(value, str):
        return datetime.date.fromisoformat(value)
    else:
        return value


class DateFunctions(ComparableFunctions):
    @property
    def year(self):
        return _apply(qm.Function.YearFromDate, self)

    @property
    def month(self):
        return _apply(qm.Function.MonthFromDate, self)

    @property
    def day(self):
        return _apply(qm.Function.DayFromDate, self)

    def difference_in_years(self, other):
        other = parse_date_if_str(other)
        return _apply(qm.Function.DateDifferenceInYears, self, other)

    def add_days(self, other):
        return _apply(qm.Function.DateAddDays, self, other)

    def subtract_days(self, other):
        return self.add_days(other.__neg__())

    def is_before(self, other):
        other = parse_date_if_str(other)
        return self < other

    def is_on_or_before(self, other):
        other = parse_date_if_str(other)
        return self <= other

    def is_after(self, other):
        other = parse_date_if_str(other)
        return self > other

    def is_on_or_after(self, other):
        other = parse_date_if_str(other)
        return self >= other

    def to_first_of_year(self):
        return _apply(qm.Function.ToFirstOfYear, self)

    def to_first_of_month(self):
        return _apply(qm.Function.ToFirstOfMonth, self)


class DateAggregations(ComparableAggregations):
    "Empty for now"


class DateEventSeries(DateFunctions, DateAggregations, EventSeries):
    _type = datetime.date


class DatePatientSeries(DateFunctions, PatientSeries):
    _type = datetime.date


# CODE SERIES
#


class CodeFunctions:
    def to_category(self, categorisation):
        return self.map_values(categorisation)


class CodeEventSeries(CodeFunctions, EventSeries):
    _type = BaseCode


class CodePatientSeries(CodeFunctions, PatientSeries):
    _type = BaseCode


# CONVERT QUERY MODEL SERIES TO EHRQL SERIES
#


def _wrap(qm_node):
    """
    Wrap a query model series in the ehrQL series class appropriate for its type and
    dimension
    """
    type_ = get_series_type(qm_node)
    is_patient_level = has_one_row_per_patient(qm_node)
    try:
        cls = REGISTERED_TYPES[type_, is_patient_level]
    except KeyError:
        # If we don't have a match for exactly this type then we should have one for a
        # superclass
        matches = [
            cls
            for ((target_type, target_dimension), cls) in REGISTERED_TYPES.items()
            if issubclass(type_, target_type) and is_patient_level == target_dimension
        ]
        assert len(matches) == 1
        cls = matches[0]
    return cls(qm_node)


def _apply(qm_cls, *args):
    """
    Applies a query model operation `qm_cls` to its arguments which can be either ehrQL
    series or static values, returns an ehrQL series
    """
    # Convert all arguments into query model nodes
    qm_args = map(_convert, args)
    qm_node = qm_cls(*qm_args)
    # Wrap the resulting node back up in an ehrQL series
    return _wrap(qm_node)


def _convert(arg):
    # Unpack dictionary arguments
    if isinstance(arg, _DictArg):
        return {_convert(key): _convert(value) for key, value in arg}
    # If it's an ehrQL series then get the wrapped query model node
    elif isinstance(arg, BaseSeries):
        return arg.qm_node
    # If it's a Codelist extract the set of codes and put it in a Value wrapper
    elif isinstance(arg, Codelist):
        return qm.Value(frozenset(arg.codes))
    # Otherwise it's a static value and needs to be put in a query model Value wrapper
    else:
        return qm.Value(arg)


# FRAME TYPES
#


class BaseFrame:
    def __init__(self, qm_node):
        self.qm_node = qm_node

    def __getattr__(self, name):
        if not name.startswith("__"):
            return self._select_column(name)
        else:
            raise AttributeError(f"object has no attribute {name!r}")

    def _select_column(self, name):
        return _wrap(qm.SelectColumn(source=self.qm_node, name=name))

    def exists_for_patient(self):
        return _wrap(qm.AggregateByPatient.Exists(source=self.qm_node))

    def count_for_patient(self):
        return _wrap(qm.AggregateByPatient.Count(source=self.qm_node))


class PatientFrame(BaseFrame):
    pass


class EventFrame(BaseFrame):
    def take(self, series):
        return EventFrame(
            qm.Filter(
                source=self.qm_node,
                condition=_convert(series),
            )
        )

    def drop(self, series):
        return EventFrame(
            qm.Filter(
                source=self.qm_node,
                condition=qm.Function.Or(
                    lhs=qm.Function.Not(_convert(series)),
                    rhs=qm.Function.IsNull(_convert(series)),
                ),
            )
        )

    def sort_by(self, *order_series):
        qm_node = self.qm_node
        # We expect series to be supplied highest priority first and, as the most
        # recently applied Sort operation has the highest priority, we need to apply
        # them in reverse order
        for series in reversed(order_series):
            qm_node = qm.Sort(
                source=qm_node,
                sort_by=_convert(series),
            )
        return SortedEventFrame(qm_node)


class SortedEventFrame(BaseFrame):
    def first_for_patient(self):
        return PatientFrame(
            qm.PickOneRowPerPatient(
                position=qm.Position.FIRST,
                source=self.qm_node,
            )
        )

    def last_for_patient(self):
        return PatientFrame(
            qm.PickOneRowPerPatient(
                position=qm.Position.LAST,
                source=self.qm_node,
            )
        )


# FRAME CONSTRUCTOR ENTRYPOINTS
#


class SchemaError(Exception):
    ...


# A class decorator which replaces the class definition with an appropriately configured
# instance of the class. Obviously this is a _bit_ odd, but I think worth it overall.
# Using classes to define tables is (as far as I can tell) the only way to get nice
# autocomplete and type-checking behaviour for column names. But we don't actually want
# these classes accessible anywhere: users should only be interacting with instances of
# the classes, and having the classes themselves in the module namespaces only makes
# autocomplete more confusing and error prone.
def table(cls):
    try:
        qm_class = {
            (PatientFrame,): qm.SelectPatientTable,
            (EventFrame,): qm.SelectTable,
        }[cls.__bases__]
    except KeyError:
        raise SchemaError(
            "Schema class must subclass either `PatientFrame` or `EventFrame`"
        )

    table_name = cls.__name__
    # Get all `Series` objects on the class and determine the schema from them
    schema = {
        series.name: series.type_
        for series in vars(cls).values()
        if isinstance(series, Series)
    }

    qm_node = qm_class(table_name, qm.TableSchema(schema))
    return cls(qm_node)


# A descriptor which will return the appropriate type of series depending on the type of
# frame it belongs to i.e. a PatientSeries subclass for PatientFrames and an EventSeries
# subclass for EventFrames. This lets schema authors use a consistent syntax when
# defining frames of either type.
class Series:
    def __init__(
        self,
        type_,
        description="",
        constraints=(),
        required=True,
        implementation_notes_to_add_to_description="",
        notes_for_implementors="",
    ):
        self.type_ = type_
        self.description = description
        self.constraints = constraints
        self.required = required
        self.implementation_notes_to_add_to_description = (
            implementation_notes_to_add_to_description
        )
        self.notes_for_implementors = notes_for_implementors

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        # Prevent users attempting to interact with the class rather than an instance
        if instance is None:
            raise SchemaError("Missing `@table` decorator on schema class")
        return instance._select_column(self.name)


# CASE EXPRESSION FUNCTIONS
#


# TODO: There's no explicit error handling on using this wrong e.g. not calling `then()`
# or passing the wrong sort of thing as `condition`. The query model will prevent any
# invalid queries being created, but we should invest time in making the errors as
# immediate and as friendly as possible.
class when:
    def __init__(self, condition):
        self._condition = condition

    def then(self, value):
        new = self.__class__(self._condition)
        new._value = value
        return new


def case(*when_thens, default=None):
    cases = _DictArg((case._condition, case._value) for case in when_thens)
    # If we don't want a default then we shouldn't supply an argument, or else it will
    # get converted into `Value(None)` which is not what we want
    if default is None:
        return _apply(qm.Case, cases)
    else:
        return _apply(qm.Case, cases, default)
