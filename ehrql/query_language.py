import dataclasses
import datetime
import functools
import operator
import re
from collections import ChainMap
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, overload

from ehrql import serializer_registry
from ehrql.codes import BaseCode, BaseMultiCodeString
from ehrql.file_formats import read_rows
from ehrql.query_model import nodes as qm
from ehrql.query_model.column_specs import get_column_specs_from_schema
from ehrql.query_model.nodes import get_series_type, has_one_row_per_patient
from ehrql.query_model.population_validation import validate_population_definition
from ehrql.utils import date_utils
from ehrql.utils.string_utils import strip_indent


T = TypeVar("T")
CodeT = TypeVar("CodeT", bound=BaseCode)
MultiCodeStringT = TypeVar("MultiCodeStringT", bound=BaseMultiCodeString)
FloatT = TypeVar("FloatT", bound="FloatFunctions")
DateT = TypeVar("DateT", bound="DateFunctions")
IntT = TypeVar("IntT", bound="IntFunctions")
StrT = TypeVar("StrT", bound="StrFunctions")

VALID_ATTRIBUTE_NAME_RE = re.compile(r"^[A-Za-z]+[A-Za-z0-9_]*$")

TRAILING_COMMA_HINT = """
This is probably because there is a trailing comma left on one of the values.
For example, you might have:

    x = something(),

where you should have:

    x = something()"""

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


class Error(Exception):
    """
    Used to translate errors from the query model into something more
    ehrQL-appropriate
    """

    # Pretend this exception is defined in the top-level `ehrql` module: this allows us
    # to avoid leaking the internal `query_language` module into the error messages
    # without creating circular import problems.
    __module__ = "ehrql"


@dataclasses.dataclass
class DummyDataConfig:
    population_size: int = 10
    legacy: bool = False
    timeout: int = 60
    additional_population_constraint: "qm.Series[bool] | None" = None

    def set_additional_population_constraint(self, additional_population_constraint):
        if additional_population_constraint is not None:
            validate_patient_series_type(
                additional_population_constraint,
                types=[bool],
                context="additional population constraint",
            )
            self.additional_population_constraint = (
                additional_population_constraint._qm_node
            )
        if self.legacy and self.additional_population_constraint is not None:
            raise ValueError(
                "Cannot provide an additional population constraint in legacy mode."
            )


class Dataset:
    """
    To create a dataset use the [`create_dataset`](#create_dataset) function.
    """

    def __init__(self):
        # Set attributes with `object.__setattr__` to avoid using the
        # `__setattr__` method on this class, which prohibits use of these
        # attribute names
        object.__setattr__(self, "_variables", {})
        object.__setattr__(self, "dummy_data_config", DummyDataConfig())
        object.__setattr__(self, "_events", {})

    def define_population(self, population_condition):
        """
        Define the condition that patients must meet to be included in the Dataset, in
        the form of a [boolean patient series](#BoolPatientSeries).

        Example usage:
        ```python
        dataset.define_population(patients.date_of_birth < "1990-01-01")
        ```

        For more detail see the how-to guide on [defining
        populations](../how-to/define-population.md).
        """
        if hasattr(self, "population"):
            raise AttributeError(
                "define_population() should be called no more than once"
            )
        validate_patient_series_type(
            population_condition,
            types=[bool],
            context="population definition",
        )
        try:
            validate_population_definition(population_condition._qm_node)
        except qm.ValidationError as exc:
            raise Error(str(exc)) from None
        object.__setattr__(self, "population", population_condition)

    def add_column(self, column_name: str, ehrql_query):
        """
        Add a column to the dataset.

        _column_name_<br>
        The name of the new column, as a string.

        _ehrql_query_<br>
        An ehrQL query that returns one row per patient.

        Example usage:
        ```python
        dataset.add_column("age", patients.age_on("2020-01-01"))
        ```

        Using `.add_column` is equivalent to `=` for adding a single column
        but can also be used to add multiple columns, for example by iterating
        over a dictionary. For more details see the guide on
        "[How to assign multiple columns to a dataset programmatically](../how-to/assign-multiple-columns.md)".
        """
        setattr(self, column_name, ehrql_query)

    def configure_dummy_data(
        self,
        *,
        population_size=DummyDataConfig.population_size,
        legacy=DummyDataConfig.legacy,
        timeout=DummyDataConfig.timeout,
        additional_population_constraint=None,
    ):
        """
        Configure the dummy data to be generated.

        _population_size_<br>
        Maximum number of patients to generate.

        Note that you may get fewer patients than this if the generator runs out of time
        – see `timeout` below.

        _legacy_<br>
        Use legacy dummy data.

        _timeout_<br>
        Maximum time in seconds to spend generating dummy data.

        _additional_population_constraint_<br>
        An additional ehrQL query that can be used to constrain the population that will
        be selected for dummy data. This is incompatible with legacy mode.

        For example, if you wanted to ensure that two dates appear in a particular order in your
        dummy data, you could add ``additional_population_constraint = dataset.first_date <
        dataset.second_date``.

        You can also combine constraints with ``&`` as normal in ehrQL.
        E.g. ``additional_population_constraint = patients.sex.is_in(['male', 'female']) & (
        patients.age_on(some_date) < 80)`` would give you dummy data consisting of only men
        and women who were under the age of 80 on some particular date.

        Example usage:
        ```python
        dataset.configure_dummy_data(population_size=10000)
        ```
        """
        self.dummy_data_config.population_size = population_size
        self.dummy_data_config.legacy = legacy
        self.dummy_data_config.timeout = timeout
        self.dummy_data_config.set_additional_population_constraint(
            additional_population_constraint
        )

    def __setattr__(self, name, value):
        if name == "population":
            raise AttributeError(
                "Cannot set variable 'population'; use define_population() instead"
            )
        _validate_attribute_name(
            name, self._variables | self._events, context="variable"
        )
        validate_patient_series(value, context=f"variable '{name}'")
        self._variables[name] = value

    def __getattr__(self, name):
        # Make this method accessible while hiding it from autocomplete until we make it
        # generally available
        if name == "add_event_table":
            return self._internal
        if name in self._variables:
            return self._variables[name]
        if name in self._events:
            return self._events[name]
        if name == "population":
            raise AttributeError(
                "A population has not been defined; define one with define_population()"
            )
        else:
            raise AttributeError(f"Variable '{name}' has not been defined")

    # This method ought to be called `add_event_table` but we're deliberately
    # obfuscating its name for now
    def _internal(self, name, **event_series):
        _validate_attribute_name(name, self._variables | self._events, context="table")
        self._events[name] = EventTable(self, **event_series)

    def _compile(self):
        return qm.Dataset(
            population=self.population._qm_node,
            variables={k: v._qm_node for k, v in self._variables.items()},
            events={k: v._qm_node for k, v in self._events.items()},
            measures=None,
        )


class EventTable:
    def __init__(self, dataset, **series):
        # Store reference to the parent dataset to aid debug rendering
        object.__setattr__(self, "_dataset", dataset)
        object.__setattr__(self, "_series", {})
        if not series:
            raise ValueError("event tables must be defined with at least one column")
        for name, value in series.items():
            self.add_column(name, value)

    def add_column(self, name, value):
        _validate_attribute_name(name, self._series, context="column")
        validate_ehrql_series(value, context=f"column {name!r}")
        try:
            qm_node = qm.SeriesCollectionFrame(
                {
                    name: series._qm_node
                    for name, series in (self._series | {name: value}).items()
                }
            )
        except qm.PatientDomainError:
            raise TypeError(
                "event tables must have columns with more than one value per patient; "
                "for single values per patient use dataset variables"
            )
        except qm.DomainMismatchError:
            raise Error(
                "cannot combine series drawn from different tables; "
                "create a new event table for these series"
            )
        self._series[name] = value
        object.__setattr__(self, "_qm_node", qm_node)

    def __setattr__(self, name, value):
        self.add_column(name, value)

    def __getattr__(self, name):
        return self._series[name]


def _validate_attribute_name(name, defined_names, context):
    if name in defined_names:
        raise AttributeError(f"'{name}' is already set and cannot be reassigned")
    if name in ("patient_id", "population", "dummy_data_config"):
        raise AttributeError(f"'{name}' is not an allowed {context} name")
    if not VALID_ATTRIBUTE_NAME_RE.match(name):
        raise AttributeError(
            f"{context} names must start with a letter, and contain only "
            f"alphanumeric characters and underscores (you defined a "
            f"{context} '{name}')"
        )


def create_dataset():
    """
    A dataset defines the patients you want to include in your population and the
    variables you want to extract for them.

    A dataset definition file must define a dataset called `dataset`:

    ```python
    dataset = create_dataset()
    ```

    Add variables to the dataset as attributes:

    ```python
    dataset.age = patients.age_on("2020-01-01")
    ```
    """
    return Dataset()


# BASIC SERIES TYPES
#


@dataclasses.dataclass(frozen=True)
class BaseSeries:
    _qm_node: qm.Node

    def __hash__(self):
        # The issue here is not mutability but the fact that we overload `__eq__` for
        # syntatic sugar, which makes these types spectacularly ill-behaved as dict keys
        raise TypeError(f"unhashable type: {self.__class__.__name__!r}")

    def __bool__(self):
        raise TypeError(
            "The keywords 'and', 'or', and 'not' cannot be used with ehrQL, please "
            "use the operators '&', '|' and '~' instead.\n"
            "(You will also see this error if you try use a chained comparison, "
            "such as 'a < b < c'.)"
        )

    @staticmethod
    def _cast(value):
        # Series have the opportunity to cast arguments to their methods e.g. to convert
        # ISO date strings to date objects. By default, this is a no-op.
        return value

    # These are the basic operations that apply to any series regardless of type or
    # dimension
    @overload
    def __eq__(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def __eq__(self: "EventSeries", other) -> "BoolEventSeries": ...

    def __eq__(self, other):
        """
        Return a boolean series comparing each value in this series with its
        corresponding value in `other`.

        Note that the result of comparing anything with NULL (including NULL itself) is NULL.

        Example usage:
        ```python
        patients.sex == "female"
        ```
        """
        other = self._cast(other)
        return _apply(qm.Function.EQ, self, other)

    @overload
    def __ne__(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def __ne__(self: "EventSeries", other) -> "BoolEventSeries": ...
    def __ne__(self, other):
        """
        Return the inverse of `==` above.

        Note that the same point regarding NULL applies here.

        Example usage:
        ```python
        patients.sex != "unknown"
        ```
        """
        other = self._cast(other)
        return _apply(qm.Function.NE, self, other)

    @overload
    def is_null(self: "PatientSeries") -> "BoolPatientSeries": ...
    @overload
    def is_null(self: "EventSeries") -> "BoolEventSeries": ...
    def is_null(self):
        """
        Return a boolean series which is True for each NULL value in this
        series and False for each non-NULL value.

        Example usage:
        ```python
        patients.date_of_death.is_null()
        ```
        """
        return _apply(qm.Function.IsNull, self)

    @overload
    def is_not_null(self: "PatientSeries") -> "BoolPatientSeries": ...
    @overload
    def is_not_null(self: "EventSeries") -> "BoolEventSeries": ...
    def is_not_null(self):
        """
        Return the inverse of `is_null()` above.

        Example usage:
        ```python
        patients.date_of_death.is_not_null()
        ```
        """
        return self.is_null().__invert__()

    def when_null_then(self: T, other: T) -> T:
        """
        Replace any NULL value in this series with the corresponding value in `other`.

        Note that `other` must be of the same type as this series.

        Example usage:
        ```python
        (patients.date_of_death < "2020-01-01").when_null_then(False)
        ```
        """
        return case(
            when(self.is_not_null()).then(self),
            otherwise=self._cast(other),
        )

    @overload
    def is_in(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def is_in(self: "EventSeries", other) -> "BoolEventSeries": ...
    def is_in(self, other):
        """
        Return a boolean series which is True for each value in this series which is
        contained in `other`.

        See how to combine `is_in` with a codelist in
        [the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

        Example usage:
        ```python
        medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
        ```

        `other` accepts any of the standard "container" types (tuple, list, set, frozenset,
        or dict) or another event series.
        """
        if isinstance(other, tuple | list | set | frozenset | dict):
            # For iterable arguments, apply any necessary casting and convert to the
            # immutable Set type required by the query model. We don't accept arbitrary
            # iterables here because too many types in Python are iterable and there's
            # the potential for confusion amongst the less experienced of our users.
            other = frozenset(map(self._cast, other))
            return _apply(qm.Function.In, self, other)
        elif isinstance(other, EventSeries):
            # We have to use `_convert` and `_wrap` by hand here (rather than using
            # `_apply` which does this all for us) because we're constructing a
            # `CombineAsSet` query model object which doesn't have a representation in
            # the query language.
            other_as_set = qm.AggregateByPatient.CombineAsSet(_convert(other))
            return _wrap(qm.Function.In, _convert(self), other_as_set)
        elif isinstance(other, PatientSeries):
            raise TypeError(
                "Argument must be an EventSeries (i.e. have many values per patient); "
                "you supplied a PatientSeries with only one value per patient"
            )
        else:
            # If the argument is not a supported ehrQL type then we'll get an error here
            # (including hopefully helpful errors for common mistakes)
            _convert(other)
            # Otherwise it _is_ a supported type, but probably not of the right
            # cardinality
            raise TypeError(
                f"Invalid type: {type(other).__qualname__}\n"
                f"Note `is_in()` usually expects a list of values rather than a single value"
            )

    @overload
    def is_not_in(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def is_not_in(self: "EventSeries", other) -> "BoolEventSeries": ...
    def is_not_in(self, other):
        """
        Return the inverse of `is_in()` above.
        """
        return self.is_in(other).__invert__()

    def map_values(self, mapping, default=None):
        """
        Return a new series with _mapping_ applied to each value. _mapping_ should
        be a dictionary mapping one set of values to another.

        Example usage:
        ```python
        school_year = patients.age_on("2020-09-01").map_values(
            {13: "Year 9", 14: "Year 10", 15: "Year 11"},
            default="N/A"
        )
        ```
        """
        return case(
            *[
                when(self == from_value).then(to_value)
                for from_value, to_value in mapping.items()
            ],
            otherwise=default,
        )


class PatientSeries(BaseSeries):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the series using its `_type` attribute
        REGISTERED_TYPES[cls._type, True] = cls


class EventSeries(BaseSeries):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the series using its `_type` attribute
        REGISTERED_TYPES[cls._type, False] = cls

    def count_distinct_for_patient(self) -> "IntPatientSeries":
        """
        Return an [integer patient series](#IntPatientSeries) counting the number of
        distinct values for each patient in the series (ignoring any NULL values).

        Note that if a patient has no values at all in the series the result will
        be zero rather than NULL.

        Example usage:
        ```python
        medications.dmd_code.count_distinct_for_patient()
        ```
        """
        return _apply(qm.AggregateByPatient.CountDistinct, self)


# BOOLEAN SERIES
#


class BoolFunctions:
    def __and__(self: T, other: T) -> T:
        """
        Logical AND

        Return a boolean series which is True where both this series and `other` are
        True, False where either are False, and NULL otherwise.

        Example usage:
        ```python
        is_female_and_alive = patients.is_alive_on("2020-01-01") & patients.sex.is_in(["female"])
        ```
        """
        return self._apply_op_to_other(qm.Function.And, other)

    def __rand__(self: T, other: T) -> T:
        return self.__and__(other)

    def __or__(self: T, other: T) -> T:
        """
        Logical OR

        Return a boolean series which is True where either this series or `other` is
        True, False where both are False, and NULL otherwise.

        Example usage:
        ```python
        is_alive = patients.date_of_death.is_null() | patients.date_of_death.is_after("2020-01-01")
        ```
        Note that the above example is equivalent to `patients.is_alive_on("2020-01-01")`.
        """
        return self._apply_op_to_other(qm.Function.Or, other)

    def __ror__(self: T, other: T) -> T:
        return self.__or__(other)

    def _apply_op_to_other(self, op, other):
        other = self._cast(other)
        try:
            return _apply(op, self, other)
        except TypeError as exc:
            # If we've added hints to the exception then we want to re-raise it so they
            # get shown to the user. Otherwise we want to return NotImplemented so as to
            # trigger a standard "unsupported operand" error from Python.
            if getattr(exc, "__notes__", None):
                raise
            else:
                return NotImplemented

    def __invert__(self: T) -> T:
        """
        Logical NOT

        Return a boolean series which is the inverse of this series i.e. where True
        becomes False, False becomes True, and NULL stays as NULL.

        Example usage:
        ```python
        is_born_outside_period = ~ patients.date_of_birth.is_on_or_between("2020-03-01", "2020-06-30")
        ```
        """
        return _apply(qm.Function.Not, self)

    @overload
    def as_int(self: "PatientSeries") -> "IntPatientSeries": ...
    @overload
    def as_int(self: "EventSeries") -> "IntEventSeries": ...
    def as_int(self):
        """
        Return each value in this Boolean series as 1 (True) or 0 (False).
        """
        return _apply(qm.Function.CastToInt, self)


class BoolPatientSeries(BoolFunctions, PatientSeries):
    _type = bool


class BoolEventSeries(BoolFunctions, EventSeries):
    _type = bool


# METHODS COMMON TO ALL COMPARABLE TYPES
#


class ComparableFunctions:
    @overload
    def __lt__(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def __lt__(self: "EventSeries", other) -> "BoolEventSeries": ...
    def __lt__(self, other):
        """
        Return a boolean series which is True for each value in this series that is
        strictly less than its corresponding value in `other` and False otherwise (or NULL
        if either value is NULL).

        Example usage:
        ```python
        is_underage = patients.age_on("2020-01-01") < 18
        ```
        """
        other = self._cast(other)
        return _apply(qm.Function.LT, self, other)

    @overload
    def __le__(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def __le__(self: "EventSeries", other) -> "BoolEventSeries": ...
    def __le__(self, other):
        """
        Return a boolean series which is True for each value in this series that is less
        than or equal to its corresponding value in `other` and False otherwise (or NULL
        if either value is NULL).

        Example usage:
        ```python
        is_underage = patients.age_on("2020-01-01") <= 17
        ```
        """
        other = self._cast(other)
        return _apply(qm.Function.LE, self, other)

    @overload
    def __ge__(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def __ge__(self: "EventSeries", other) -> "BoolEventSeries": ...
    def __ge__(self, other):
        """
        Return a boolean series which is True for each value in this series that is
        greater than or equal to its corresponding value in `other` and False otherwise
        (or NULL if either value is NULL).

        Example usage:
        ```python
        is_adult = patients.age_on("2020-01-01") >= 18
        ```
        """
        other = self._cast(other)
        return _apply(qm.Function.GE, self, other)

    @overload
    def __gt__(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def __gt__(self: "EventSeries", other) -> "BoolEventSeries": ...
    def __gt__(self, other):
        """
        Return a boolean series which is True for each value in this series that is
        strictly greater than its corresponding value in `other` and False otherwise (or
        NULL if either value is NULL).

        Example usage:
        ```python
        is_adult = patients.age_on("2020-01-01") > 17
        ```
        """
        other = self._cast(other)
        return _apply(qm.Function.GT, self, other)


class ComparableAggregations:
    @overload
    def minimum_for_patient(self: DateT) -> "DatePatientSeries": ...
    @overload
    def minimum_for_patient(self: StrT) -> "StrPatientSeries": ...
    @overload
    def minimum_for_patient(self: IntT) -> "IntPatientSeries": ...
    @overload
    def minimum_for_patient(self: FloatT) -> "FloatPatientSeries": ...
    def minimum_for_patient(self):
        """
        Return the minimum value in the series for each patient (or NULL if the patient
        has no values).

        Example usage:
        ```python
        clinical_events.where(...).numeric_value.minimum_for_patient()
        ```
        """
        return _apply(qm.AggregateByPatient.Min, self)

    @overload
    def maximum_for_patient(self: DateT) -> "DatePatientSeries": ...
    @overload
    def maximum_for_patient(self: StrT) -> "StrPatientSeries": ...
    @overload
    def maximum_for_patient(self: IntT) -> "IntPatientSeries": ...
    @overload
    def maximum_for_patient(self: FloatT) -> "FloatPatientSeries": ...
    def maximum_for_patient(self):
        """
        Return the maximum value in the series for each patient (or NULL if the patient
        has no values).

        Example usage:
        ```python
        clinical_events.where(...).numeric_value.maximum_for_patient()
        ```
        """
        return _apply(qm.AggregateByPatient.Max, self)


# STRING SERIES
#


class StrFunctions(ComparableFunctions):
    @overload
    def contains(self: "PatientSeries", other) -> "BoolPatientSeries": ...
    @overload
    def contains(self: "EventSeries", other) -> "BoolEventSeries": ...
    def contains(self, other):
        """
        Return a boolean series which is True for each string in this series which
        contains `other` as a sub-string and False otherwise. For NULL values, the
        result is NULL.

        Example usage:
        ```python
        is_female = patients.sex.contains("fem")
        ```

        `other` can be another string series, in which case corresponding values
        are compared. If either value is NULL the result is NULL.
        """
        other = self._cast(other)
        return _apply(qm.Function.StringContains, self, other)


class StrAggregations(ComparableAggregations):
    "Empty for now"


class StrPatientSeries(StrFunctions, PatientSeries):
    _type = str


class StrEventSeries(StrFunctions, StrAggregations, EventSeries):
    _type = str


# NUMERIC SERIES
#


class NumericFunctions(ComparableFunctions):
    @overload
    def __add__(self: IntT, other: IntT | int) -> IntT: ...
    @overload
    def __add__(self: FloatT, other: FloatT | float) -> FloatT: ...
    def __add__(self, other):
        """
        Return the sum of each corresponding value in this series and `other` (or NULL
        if either is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.Add, self, other)

    @overload
    def __radd__(self: IntT, other: IntT | int) -> IntT: ...
    @overload
    def __radd__(self: FloatT, other: FloatT | float) -> FloatT: ...
    def __radd__(self, other):
        return self + other

    @overload
    def __sub__(self: IntT, other: IntT | int) -> IntT: ...
    @overload
    def __sub__(self: FloatT, other: FloatT | float) -> FloatT: ...
    def __sub__(self, other):
        """
        Return each value in this series with its corresponding value in `other`
        subtracted (or NULL if either is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.Subtract, self, other)

    @overload
    def __rsub__(self: IntT, other: IntT | int) -> IntT: ...
    @overload
    def __rsub__(self: FloatT, other: FloatT | float) -> FloatT: ...
    def __rsub__(self, other):
        return other + -self

    @overload
    def __mul__(self: IntT, other: IntT | int) -> IntT: ...
    @overload
    def __mul__(self: FloatT, other: FloatT | float) -> FloatT: ...
    def __mul__(self, other):
        """
        Return the product of each corresponding value in this series and `other` (or
        NULL if either is NULL).
        """
        other = self._cast(other)
        return _apply(qm.Function.Multiply, self, other)

    @overload
    def __rmul__(self: IntT, other: IntT | int) -> IntT: ...
    @overload
    def __rmul__(self: FloatT, other: FloatT | float) -> FloatT: ...
    def __rmul__(self, other):
        return self * other

    @overload
    def __truediv__(self: "PatientSeries", other) -> "FloatPatientSeries": ...
    @overload
    def __truediv__(self: "EventSeries", other) -> "FloatEventSeries": ...
    def __truediv__(self, other):
        """
        Return a series with each value in this series divided by its correponding value
        in `other` (or NULL if either is NULL).

        Note that the result is always if a float even if the inputs are integers.
        """
        other = self._cast(other)
        return _apply(qm.Function.TrueDivide, self, other)

    @overload
    def __rtruediv__(self: "PatientSeries", other) -> "FloatPatientSeries": ...
    @overload
    def __rtruediv__(self: "EventSeries", other) -> "FloatEventSeries": ...
    def __rtruediv__(self, other):
        return self / other

    @overload
    def __floordiv__(self: "PatientSeries", other) -> "IntPatientSeries": ...
    @overload
    def __floordiv__(self: "EventSeries", other) -> "IntEventSeries": ...
    def __floordiv__(self, other):
        """
        Return a series with each value in this series divided by its correponding value
        in `other` and then rounded **down** to the nearest integer value (or NULL if either
        is NULL).

        Note that the result is always if an integer even if the inputs are floats.
        """
        other = self._cast(other)
        return _apply(qm.Function.FloorDivide, self, other)

    @overload
    def __rfloordiv__(self: "PatientSeries", other) -> "IntPatientSeries": ...
    @overload
    def __rfloordiv__(self: "EventSeries", other) -> "IntEventSeries": ...
    def __rfloordiv__(self, other):
        return self // other

    def __neg__(self: T) -> T:
        """
        Return the negation of each value in this series.
        """
        return _apply(qm.Function.Negate, self)

    def absolute(self: T) -> T:
        """
        Return the absolute value of each value in this series (i.e. make any negative
        values positive).

        Example usage:
        ```python
        date_diff_days = (event_1_date - event_2_date).days
        within_14_days = date_diff_days.absolute() <= 14
        ```
        """
        return _apply(qm.Function.Absolute, self)

    def __abs__(self):
        raise Error("Instead of `abs(x)` use `x.absolute()`")

    @overload
    def as_int(self: "PatientSeries") -> "IntPatientSeries": ...
    @overload
    def as_int(self: "EventSeries") -> "IntEventSeries": ...
    def as_int(self):
        """
        Return each value in this series rounded down to the nearest integer.
        """
        return _apply(qm.Function.CastToInt, self)

    @overload
    def as_float(self: "PatientSeries") -> "FloatPatientSeries": ...
    @overload
    def as_float(self: "EventSeries") -> "FloatEventSeries": ...
    def as_float(self):
        """
        Return each value in this series as a float (e.g. 10 becomes 10.0).
        """
        return _apply(qm.Function.CastToFloat, self)


class NumericAggregations(ComparableAggregations):
    @overload
    def sum_for_patient(self: FloatT) -> "FloatPatientSeries": ...
    @overload
    def sum_for_patient(self: IntT) -> "IntPatientSeries": ...
    def sum_for_patient(self):
        """
        Return the sum of all values in the series for each patient.
        """
        return _apply(qm.AggregateByPatient.Sum, self)

    def mean_for_patient(self) -> "FloatPatientSeries":
        """
        Return the arithmetic mean of any non-NULL values in the series for each
        patient.
        """
        return _apply(qm.AggregateByPatient.Mean, self)


class IntFunctions(NumericFunctions):
    "Currently only needed for type hints to easily tell the difference between int and float series"


class IntPatientSeries(IntFunctions, PatientSeries):
    _type = int


class IntEventSeries(IntFunctions, NumericAggregations, EventSeries):
    _type = int


class FloatFunctions(NumericFunctions):
    @staticmethod
    def _cast(value):
        """
        Casting int literals to floats. We do not support casting to float for IntSeries.
        """
        if isinstance(value, int):
            return float(value)
        return value


class FloatPatientSeries(FloatFunctions, PatientSeries):
    _type = float


class FloatEventSeries(FloatFunctions, NumericAggregations, EventSeries):
    _type = float


# DATE SERIES
#


def parse_date_if_str(value):
    if isinstance(value, str):
        # By default, `fromisoformat()` accepts the alternative YYYYMMDD format. We only
        # want to allow the hyphenated version so we pre-validate it.
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError(f"Dates must be in YYYY-MM-DD format: {value!r}")
        try:
            return datetime.date.fromisoformat(value)
        except ValueError as e:
            raise ValueError(f"{e} in {value!r}") from None
    else:
        return value


def cast_all_arguments(args):
    series_args = [arg for arg in args if isinstance(arg, BaseSeries)]
    if series_args:
        # Choose the first series arbitrarily, the type checker will enforce that they
        # are all the same type in any case
        cast = series_args[0]._cast
        return tuple(map(cast, args))
    else:
        # This would only be the case if all the arguments were literals, which would be
        # an unusual and pointless bit of ehrQL, but we should handle it without error
        return args


# This allows us to get type hints for properties by replacing the
# @property decorator with this decorator. Currently only needed for
# ints. We pass the docstring through so that it can appear in the docs
class int_property[T]:
    def __init__(self, getter: Callable[[Any], T]) -> None:
        self.__doc__ = getter.__doc__
        self.getter = getter

    def __set__(self, instance, value): ...

    @overload
    def __get__(self, obj: PatientSeries, objtype=None) -> "IntPatientSeries": ...

    @overload
    def __get__(self, obj: EventSeries, objtype=None) -> "IntEventSeries": ...

    def __get__(self, obj, objtype=None):
        return self.getter(obj)


class DateFunctions(ComparableFunctions):
    @staticmethod
    def _cast(value):
        return parse_date_if_str(value)

    @int_property
    def year(self):
        """
        Return an integer series giving the year of each date in this series.
        """
        return _apply(qm.Function.YearFromDate, self)

    @int_property
    def month(self):
        """
        Return an integer series giving the month (1-12) of each date in this series.
        """
        return _apply(qm.Function.MonthFromDate, self)

    @int_property
    def day(self):
        """
        Return an integer series giving the day of the month (1-31) of each date in this
        series.
        """
        return _apply(qm.Function.DayFromDate, self)

    def to_first_of_year(self: T) -> T:
        """
        Return a date series with each date in this series replaced by the date of the
        first day in its corresponding calendar year.

        Example usage:
        ```python
        patients.date_of_death.to_first_of_year()
        ```
        """
        return _apply(qm.Function.ToFirstOfYear, self)

    def to_first_of_month(self: T) -> T:
        """
        Return a date series with each date in this series replaced by the date of the
        first day in its corresponding calendar month.

        Example usage:
        ```python
        patients.date_of_death.to_first_of_month()
        ```
        """
        return _apply(qm.Function.ToFirstOfMonth, self)

    @overload
    def is_before(self: PatientSeries, other) -> BoolPatientSeries: ...
    @overload
    def is_before(self: EventSeries, other) -> BoolEventSeries: ...
    def is_before(self, other):
        """
        Return a boolean series which is True for each date in this series that is
        strictly earlier than its corresponding date in `other` and False otherwise
        (or NULL if either value is NULL).

        Example usage:
        ```python
        medications.where(medications.date.is_before("2020-04-01"))
        ```
        """
        return self.__lt__(other)

    @overload
    def is_on_or_before(self: PatientSeries, other) -> BoolPatientSeries: ...
    @overload
    def is_on_or_before(self: EventSeries, other) -> BoolEventSeries: ...
    def is_on_or_before(self, other):
        """
        Return a boolean series which is True for each date in this series that is
        earlier than or the same as its corresponding value in `other` and False
        otherwise (or NULL if either value is NULL).

        Example usage:
        ```python
        medications.where(medications.date.is_on_or_before("2020-03-31"))
        ```
        """
        return self.__le__(other)

    @overload
    def is_after(self: PatientSeries, other) -> BoolPatientSeries: ...
    @overload
    def is_after(self: EventSeries, other) -> BoolEventSeries: ...
    def is_after(self, other):
        """
        Return a boolean series which is True for each date in this series that is
        strictly later than its corresponding date in `other` and False otherwise
        (or NULL if either value is NULL).

        Example usage:
        ```python
        medications.where(medications.date.is_after("2020-03-31"))
        ```
        """
        return self.__gt__(other)

    @overload
    def is_on_or_after(self: PatientSeries, other) -> BoolPatientSeries: ...
    @overload
    def is_on_or_after(self: EventSeries, other) -> BoolEventSeries: ...
    def is_on_or_after(self, other):
        """
        Return a boolean series which is True for each date in this series that is later
        than or the same as its corresponding value in `other` and False otherwise (or
        NULL if either value is NULL).

        Example usage:
        ```python
        medications.where(medications.date.is_on_or_after("2020-04-01"))
        ```
        """
        return self.__ge__(other)

    @overload
    def is_between_but_not_on(self: PatientSeries, start, end) -> BoolPatientSeries: ...
    @overload
    def is_between_but_not_on(self: EventSeries, start, end) -> BoolEventSeries: ...
    def is_between_but_not_on(self, start, end):
        """
        Return a boolean series which is True for each date in this series which is
        strictly between (i.e. not equal to) the corresponding dates in `start` and `end`,
        and False otherwise.

        Example usage:
        ```python
        medications.where(medications.date.is_between_but_not_on("2020-03-31", "2021-04-01"))
        ```
        For each trio of dates being compared, if any date is NULL the result is NULL.
        """
        return (self > start) & (self < end)

    @overload
    def is_on_or_between(self: PatientSeries, start, end) -> BoolPatientSeries: ...
    @overload
    def is_on_or_between(self: EventSeries, start, end) -> BoolEventSeries: ...
    def is_on_or_between(self, start, end):
        """
        Return a boolean series which is True for each date in this series which is
        between or the same as the corresponding dates in `start` and `end`, and
        False otherwise.

        Example usage:
        ```python
        medications.where(medications.date.is_on_or_between("2020-04-01", "2021-03-31"))
        ```
        For each trio of dates being compared, if any date is NULL the result is NULL.
        """
        return (self >= start) & (self <= end)

    @overload
    def is_during(self: PatientSeries, interval) -> BoolPatientSeries: ...
    @overload
    def is_during(self: EventSeries, interval) -> BoolEventSeries: ...
    def is_during(self, interval):
        """
        The same as `is_on_or_between()` above, but allows supplying a start/end date
        pair as single argument.

        Example usage:
        ```python
        study_period = ("2020-04-01", "2021-03-31")
        medications.where(medications.date.is_during(study_period))
        ```

        Also see the docs on using `is_during` with the
        [`INTERVAL` placeholder](../explanation/measures.md/#the-interval-placeholder).
        """
        start, end = interval
        return self.is_on_or_between(start, end)

    def __sub__(self, other):
        """
        Return a series giving the difference between each date in this series and
        `other` (see [`DateDifference`](#DateDifference)).

        Example usage:
        ```python
        age_months = (date("2020-01-01") - patients.date_of_birth).months
        ```
        """
        other = self._cast(other)
        if isinstance(other, datetime.date | DateEventSeries | DatePatientSeries):
            return DateDifference(self, other)
        else:
            return NotImplemented

    def __rsub__(self, other):
        other = self._cast(other)
        if isinstance(other, datetime.date | DateEventSeries | DatePatientSeries):
            return DateDifference(other, self)
        else:
            return NotImplemented


class DateAggregations(ComparableAggregations):
    def count_episodes_for_patient(self, maximum_gap) -> IntPatientSeries:
        """
        Counts the number of "episodes" for each patient where dates which are no more
        than `maximum_gap` apart are considered part of the same episode. The
        `maximum_gap` duration can be specified in [`days()`](#days) or
        [`weeks()`](#weeks).

        For example, suppose a patient has the following sequence of events:

        Event ID | Date
        -- | --
        A | 2020-01-01
        B | 2020-01-04
        C | 2020-01-06
        D | 2020-01-10
        E | 2020-01-12

        And suppose we count the episodes here using a maximum gap of three days:
        ```python
        .count_episodes_for_patient(days(3))
        ```

        We will get an episode count of two: events A, B and C are considered as one
        episode and events D and E as another.

        Note that events A and C are considered part of the same episode even though
        they are more than three days apart because event B is no more than three days
        apart from both of them. That is, the clock restarts with each new event in an
        episode rather than running from the first event in an episode.
        """
        if isinstance(maximum_gap, days):
            maximum_gap_days = maximum_gap.value
        elif isinstance(maximum_gap, weeks):
            maximum_gap_days = maximum_gap.value * 7
        else:
            raise TypeError("`maximum_gap` must be supplied as `days()` or `weeks()`")
        if not isinstance(maximum_gap_days, int):
            raise ValueError(
                f"`maximum_gap` must be a single, fixed number of "
                f"{type(maximum_gap).__name__}"
            )
        return _wrap(
            qm.AggregateByPatient.CountEpisodes,
            source=self._qm_node,
            maximum_gap_days=maximum_gap_days,
        )


class DatePatientSeries(DateFunctions, PatientSeries):
    _type = datetime.date


class DateEventSeries(DateFunctions, DateAggregations, EventSeries):
    _type = datetime.date


# The default dataclass equality method doesn't work here and while we could define our
# own it wouldn't be very useful for this type
@dataclasses.dataclass(eq=False)
class DateDifference:
    """
    Represents the difference between two dates or date series (i.e. it is what you
    get when you perform subtractions on [DatePatientSeries](#DatePatientSeries.sub)
    or [DateEventSeries](#DateEventSeries.sub)).
    """

    lhs: datetime.date | DateEventSeries | DatePatientSeries
    rhs: datetime.date | DateEventSeries | DatePatientSeries

    @property
    def days(self):
        """
        The value of the date difference in days (can be positive or negative).
        """
        return _apply(qm.Function.DateDifferenceInDays, self.lhs, self.rhs)

    @property
    def weeks(self):
        """
        The value of the date difference in whole weeks (can be positive or negative).
        """
        return self.days // 7

    @property
    def months(self):
        """
        The value of the date difference in whole calendar months (can be positive or
        negative).
        """
        return _apply(qm.Function.DateDifferenceInMonths, self.lhs, self.rhs)

    @property
    def years(self):
        """
        The value of the date difference in whole calendar years (can be positive or
        negative).
        """
        return _apply(qm.Function.DateDifferenceInYears, self.lhs, self.rhs)


@dataclasses.dataclass
class Duration:
    value: int | IntEventSeries | IntPatientSeries

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        assert cls._date_add_static is not None
        assert cls._date_add_qm is not None

    # The default dataclass equality/inequality methods don't behave correctly here
    def __eq__(self, other) -> bool:
        """
        Return True if `other` has the same value and units, and False otherwise.

        Hence, the result of `weeks(1) == days(7)` will be False.
        """
        if other.__class__ is not self.__class__:
            return False
        return self.value == other.value

    def __ne__(self, other) -> bool:
        """
        Return the inverse of `==` above.
        """
        # We have to apply different inversion logic depending on whether we have a
        # boolean or a BoolSeries
        is_equal = self == other
        if isinstance(is_equal, bool):
            return not is_equal
        else:
            return is_equal.__invert__()

    def __add__(self, other: T) -> T:
        """
        If `other` is a date or date series, add this duration to `other`
        to produce a new date.

        If `other` is another duration with the same units, add the two durations
        together to produce a new duration.
        """
        other = parse_date_if_str(other)
        if isinstance(self.value, int) and isinstance(other, datetime.date):
            # If both operands are static values we can perform the date arithmetic
            # directly ourselves
            return self._date_add_static(other, self.value)
        elif isinstance(other, datetime.date | DateEventSeries | DatePatientSeries):
            # Otherwise we create the appropriate query model construct
            return _apply(self._date_add_qm, other, self.value)
        elif isinstance(other, self.__class__):
            # Durations of the same type can be added together
            return self.__class__(self.value + other.value)
        else:
            # Nothing else is handled
            return NotImplemented

    def __sub__(self, other: T) -> T:
        """
        Subtract `other` from this duration. `other` must be a
        duration in the same units.
        """
        return self.__add__(other.__neg__())

    def __radd__(self, other: T) -> T:
        return self.__add__(other)

    def __rsub__(self, other: T) -> T:
        return self.__neg__().__add__(other)

    def __neg__(self: T) -> T:
        """
        Invert this duration, i.e. count the duration backwards in time
        if it was originally forwards, and vice versa.
        """
        return self.__class__(self.value.__neg__())

    def starting_on(self, date) -> list[tuple[datetime.date, datetime.date]]:
        """
        Return a list of time intervals covering the duration starting on
        `date`. Each interval lasts one unit.

        Example usage:
        ```python
        weeks(3).starting_on("2000-01-01")
        ```
        The above would return:
        ```
        [
            (date(2000, 1, 1), date(2000, 1, 7)),
            (date(2000, 1, 8), date(2000, 1, 14)),
            (date(2000, 1, 15), date(2000, 1, 21)),
        ]
        ```

        Useful for generating the `intervals` arguments to [`Measures`](#Measures).
        """
        return self._generate_intervals(date, self.value, 1, "starting_on")

    def ending_on(self, date) -> list[tuple[datetime.date, datetime.date]]:
        """
        Return a list of time intervals covering the duration ending on
        `date`. Each interval lasts one unit.

        Example usage:
        ```python
        weeks(3).ending_on("2000-01-21")
        ```
        The above would return:
        ```
        [
            (date(2000, 1, 1), date(2000, 1, 7)),
            (date(2000, 1, 8), date(2000, 1, 14)),
            (date(2000, 1, 15), date(2000, 1, 21)),
        ]
        ```

        Useful for generating the `intervals` arguments to [`Measures`](#Measures).
        """
        return self._generate_intervals(date, self.value, -1, "ending_on")

    @classmethod
    def _generate_intervals(cls, date, value, sign, method_name):
        date = parse_date_if_str(date)
        if not isinstance(date, datetime.date):
            raise TypeError(
                f"{cls.__name__}.{method_name}() can only be used with a literal "
                f"date, not a date series"
            )
        if not isinstance(value, int):
            raise TypeError(
                f"{cls.__name__}.{method_name}() can only be used with a literal "
                f"integer value, not an integer series"
            )
        if value < 0:
            raise ValueError(
                f"{cls.__name__}.{method_name}() can only be used with positive numbers"
            )
        return date_utils.generate_intervals(cls._date_add_static, date, value * sign)


class days(Duration):
    """
    Represents a duration of time specified in days.

    Example usage:
    ```python
    last_medication_date = medications.sort_by(medications.date).last_for_patient().date
    start_date = last_medication_date - days(90)
    end_date = last_medication_date + days(90)
    ```
    """

    _date_add_static = staticmethod(date_utils.date_add_days)
    _date_add_qm = qm.Function.DateAddDays


class weeks(Duration):
    """
    Represents a duration of time specified in weeks.

    Example usage:
    ```python
    last_medication_date = medications.sort_by(medications.date).last_for_patient().date
    start_date = last_medication_date - weeks(12)
    end_date = last_medication_date + weeks(12)
    ```
    """

    _date_add_static = staticmethod(date_utils.date_add_weeks)

    @staticmethod
    def _date_add_qm(date, num_weeks):
        num_days = qm.Function.Multiply(num_weeks, qm.Value(7))
        return qm.Function.DateAddDays(date, num_days)


class months(Duration):
    """
    Represents a duration of time specified in calendar months.

    Example usage:
    ```python
    last_medication_date = medications.sort_by(medications.date).last_for_patient().date
    start_date = last_medication_date - months(3)
    end_date = last_medication_date + months(3)
    ```

    Consider using [`days()`](#days) or [`weeks()`](#weeks) instead -
    see the section on [Ambiguous Dates](#ambiguous-dates) for more.
    """

    _date_add_static = staticmethod(date_utils.date_add_months)
    _date_add_qm = qm.Function.DateAddMonths


class years(Duration):
    """
    Represents a duration of time specified in calendar years.

    Example usage:
    ```python
    last_medication_date = medications.sort_by(medications.date).last_for_patient().date
    start_date = last_medication_date - years(1)
    end_date = last_medication_date + years(1)
    ```

    Consider using [`days()`](#days) or [`weeks()`](#weeks) instead -
    see the section on [Ambiguous Dates](#ambiguous-dates) for more.
    """

    _date_add_static = staticmethod(date_utils.date_add_years)
    _date_add_qm = qm.Function.DateAddYears


# CODE SERIES
#


class CodeFunctions:
    def _cast(self, value):
        if isinstance(value, str):
            return self._type(value)
        else:
            return value

    def to_category(self, categorisation, default=None):
        """
        An alias for `map_values` which makes the intention clearer when working with
        codelists.

        For more detail see [`codelist_from_csv()`](#codelist_from_csv) and the
        [how-to guide](../how-to/examples.md/#using-codelists-with-category-columns).
        """
        return self.map_values(categorisation, default=default)


class CodePatientSeries(CodeFunctions, PatientSeries):
    _type = BaseCode


class CodeEventSeries(CodeFunctions, EventSeries):
    _type = BaseCode


class MultiCodeStringFunctions:
    def _cast(self, value):
        code_type = self._type._code_type()

        if isinstance(value, code_type):
            # The passed code is of the expected type, so can convert to a string
            return value._to_primitive_type()
        elif isinstance(value, str) and self._type.is_valid(value):
            # A string that matches the regex for this type
            return value
        else:
            raise TypeError(
                f"Expecting a {code_type}, or a string prefix of a {code_type}"
            )

    def __eq__(self, other):
        """
        This operation is not allowed because it is unlikely you would want to match the
        values in this field with an exact string e.g.
        ```python
        apcs.all_diagnoses == "||I302, K201, J180 || I302, K200, M920"
        ```
        Instead you should use the `contains` or `contains_any_of` methods.
        """
        raise TypeError(
            "This column contains multiple clinical codes combined together in a single "
            "string. If you want to know if a particular code is contained in the string, "
            "please use the `contains()` method"
        )

    def __ne__(self, other):
        """
        See above.
        """
        raise TypeError(
            "This column contains multiple clinical codes combined together in a single "
            "string. If you want to know if a particular code is not contained in the string, "
            "please use the `contains()` method."
        )

    def is_in(self, other):
        """
        This operation is not allowed. To check for the presence of any codes in
        a codelist, please use the `contains_any_of(codelist)` method instead.
        """
        raise TypeError(
            "You are attempting to use `.is_in()` on a column that contains multiple "
            "clinical codes joined together. This is not allowed. If you want to know "
            "if the field contains any of the codes from a codelist, then please use "
            "`.contains_any_of(codelist)` instead."
        )

    def is_not_in(self, other):
        """
        This operation is not allowed. To check for the absence of all codes in a codelist,
        from a column called `column`, please use `~column.contains_any_of(codelist)`.
        NB the `contains_any_of(codelist)` will provide any records that contain any of the
        codes, which is then negated with the `~` operator.
        """
        raise TypeError(
            "You are attempting to use `.is_not_in()` on a column that contains multiple "
            "clinical codes joined together. This is not allowed. If you want to know "
            "if the column does not contain any of the codes from a codelist, then please use "
            "`~column.contains_any_of(codelist)` instead."
        )

    @overload
    def contains(self: PatientSeries, code) -> BoolPatientSeries: ...
    @overload
    def contains(self: EventSeries, code) -> BoolEventSeries: ...
    def contains(self, code):
        """
        Check if the multi code field contains a specific code string and return the
        result as a boolean series. `code` can be a partial match (so e.g. "N17" in
        ICD-10 would match all acute renal failure codes), or a full clinical code.

        Example usages:
        ```python
        all_diagnoses.contains("N17")
        all_diagnoses.contains("N170")
        ```
        """
        code = self._cast(code)
        return _apply(qm.Function.StringContains, self, code)

    @overload
    def contains_any_of(self: PatientSeries, codelist) -> BoolPatientSeries: ...
    @overload
    def contains_any_of(self: EventSeries, codelist) -> BoolEventSeries: ...
    def contains_any_of(self, codelist):
        """
        Check if any of the codes in `codelist` occur in the multi code field and
        return the result as a boolean series.
        As with the `contains(code)` method, the codelist can be a mixture of full
        codes and prefixes, as seen in the example below.

        Example usage:
        ```python
        all_diagnoses.contains_any_of(["N170", "N17"])
        ```
        """
        conditions = [self.contains(code) for code in codelist]
        return functools.reduce(operator.or_, conditions)


class MultiCodeStringPatientSeries(MultiCodeStringFunctions, PatientSeries):
    _type = BaseMultiCodeString


class MultiCodeStringEventSeries(MultiCodeStringFunctions, EventSeries):
    _type = BaseMultiCodeString


# CONVERT QUERY MODEL SERIES TO EHRQL SERIES
#


def _wrap(qm_cls, *args, **kwargs):
    """
    Construct a query model series and wrap it in the ehrQL series class appropriate for
    its type and dimension
    """
    qm_node = _build(qm_cls, *args, **kwargs)
    type_ = get_series_type(qm_node)
    is_patient_level = has_one_row_per_patient(qm_node)
    try:
        cls = REGISTERED_TYPES[type_, is_patient_level]
        return cls(qm_node)
    except KeyError:
        # If we don't have a match for exactly this type then we should have one for a
        # superclass. In the case where there are multiple matches, we want the narrowest
        # match. E.g. for ICD10MultiCodeString which inherits from BaseMultiCodeString,
        # which in turn inherits from str, we want to match BaseMultiCodeString as it
        # corresponds to the "closest" series match (in this case MultiCodeStringEventSeries
        # rather than the more generic StrEventSeries)
        matches = [
            {"cls": cls, "depth": type_.__mro__.index(target_type)}
            for ((target_type, target_dimension), cls) in REGISTERED_TYPES.items()
            if issubclass(type_, target_type) and is_patient_level == target_dimension
        ]
        assert matches, f"No matching query language class for {type_}"
        matches.sort(key=lambda k: k["depth"])
        cls = matches[0]["cls"]
        wrapped = cls(qm_node)
        wrapped._type = type_
        return wrapped


def _build(qm_cls, *args, **kwargs):
    "Construct a query model node, translating any errors as appropriate"
    try:
        return qm_cls(*args, **kwargs)
    except qm.InvalidSortError:
        raise Error(
            "Cannot sort by a constant value"
            # Use `from None` to hide the chained exception
        ) from None
    except qm.DomainMismatchError:
        hints = (
            " * Reduce one series to have only one value per patient by using\n"
            "   an aggregation like `maximum_for_patient()`.\n\n"
            " * Pick a single row for each patient from the table using\n"
            "   `first_for_patient()`."
        )
        if qm_cls is qm.Function.EQ:
            hints = (
                " * Use `x.is_in(y)` instead of `x == y` to check if values from\n"
                "   one series match any of the patient's values in the other.\n\n"
                f"{hints}"
            )
        raise Error(
            "\n"
            "Cannot combine series which are drawn from different tables and both\n"
            "have more than one value per patient.\n"
            "\n"
            "To address this, try one of the following:\n"
            "\n"
            f"{hints}"
            # Use `from None` to hide the chained exception
        ) from None
    except qm.TypeValidationError as exc:
        # We deliberately omit information about the query model operation and field
        # name here because these often don't match what's used in ehrQL and are liable
        # to cause confusion
        new_exc = TypeError(
            f"Expected type '{_format_typespec(exc.expected)}' "
            f"but got '{_format_typespec(exc.received)}'"
        )
        # If the value we got looks like what we were expecting except wrapped in a
        # single-member tuple then most probably the user has left a trailing comma on
        # the value
        if exc.received == tuple[exc.expected] and len(exc.value) == 1:
            new_exc.add_note(TRAILING_COMMA_HINT)
        # Use `from None` to hide the chained exception
        raise new_exc from None


def _format_typespec(typespec):
    # At present we don't do anything beyond formatting as a string and then removing
    # the module name prefix from "Series". It might be nice to remove mention of
    # "Series" entirely here, but that's a task for another day.
    return str(typespec).replace(f"{qm.__name__}.{qm.Series.__qualname__}", "Series")


def _apply(qm_cls, *args):
    """
    Applies a query model operation `qm_cls` to its arguments which can be either ehrQL
    series or static values, returns an ehrQL series
    """
    # Convert all arguments into query model nodes
    qm_args = map(_convert, args)
    # Construct the query model node and wrap it back up in an ehrQL series
    return _wrap(qm_cls, *qm_args)


def _convert(arg):
    # Pass null values through unchanged
    if arg is None:
        return None
    # Unpack tuple arguments
    elif isinstance(arg, tuple):
        return tuple(_convert(a) for a in arg)
    # If it's an ehrQL series then get the wrapped query model node
    elif isinstance(arg, BaseSeries):
        return arg._qm_node
    # If it's a static value then we need to be put in a query model Value wrapper
    elif isinstance(
        arg, bool | int | float | datetime.date | str | BaseCode | frozenset
    ):
        return qm.Value(arg)
    else:
        raise_helpful_error_if_possible(arg)
        raise TypeError(f"Not a valid ehrQL type: {arg!r}")


def Parameter(name, type_):
    """
    Return a parameter or placeholder series which can be used to construct a query
    "template": a structure which can be turned into a query by substituting in concrete
    values for any parameters it contains
    """
    return _wrap(qm.Parameter, name, type_)


# FRAME TYPES
#


class BaseFrame:
    def __init__(self, qm_node):
        self._qm_node = qm_node

    def _select_column(self, name):
        return _wrap(qm.SelectColumn, source=self._qm_node, name=name)

    def exists_for_patient(self) -> BoolPatientSeries:
        """
        Return a [boolean patient series](#BoolPatientSeries) which is True for each
        patient that has a row in this frame and False otherwise.

        Example usage:
        ```python
        pratice_registrations.for_patient_on("2020-01-01").exists_for_patient()
        ```
        """
        return _wrap(qm.AggregateByPatient.Exists, source=self._qm_node)

    def count_for_patient(self) -> IntPatientSeries:
        """
        Return an [integer patient series](#IntPatientSeries) giving the number of rows each
        patient has in this frame.

        Note that if a patient has no rows at all in the frame the result will be zero
        rather than NULL.

        Example usage:
        ```python
        clinical_events.where(clinical_events.date.year == 2020).count_for_patient()
        ```
        """
        return _wrap(qm.AggregateByPatient.Count, source=self._qm_node)


class PatientFrame(BaseFrame):
    """
    Frame containing at most one row per patient.
    """


class EventFrame(BaseFrame):
    """
    Frame which may contain multiple rows per patient.
    """

    def where(self, condition):
        """
        Return a new frame containing only the rows in this frame for which `condition`
        evaluates True.

        Note that this excludes any rows for which `condition` is NULL.

        Example usage:
        ```python
        clinical_events.where(clinical_events.date >= "2020-01-01")
        ```
        """
        return self.__class__(
            qm.Filter(
                source=self._qm_node,
                condition=_convert(condition),
            )
        )

    def except_where(self, condition):
        """
        Return a new frame containing only the rows in this frame for which `condition`
        evaluates False or NULL i.e. the exact inverse of the rows included by
        `where()`.

        Example usage:
        ```python
        practice_registrations.except_where(practice_registrations.end_date < "2020-01-01")
        ```

        Note that `except_where()` is not the same as `where()` with an inverted condition,
        as the latter would exclude rows where `condition` is NULL.
        """
        return self.__class__(
            qm.Filter(
                source=self._qm_node,
                condition=qm.Function.Or(
                    lhs=qm.Function.Not(_convert(condition)),
                    rhs=qm.Function.IsNull(_convert(condition)),
                ),
            )
        )

    def sort_by(self, *sort_values):
        """
        Return a new frame with the rows sorted for each patient, by
        each of the supplied `sort_values`.

        Where more than one sort value is supplied then the first (i.e. left-most) value
        has highest priority and each subsequent sort value will only be used as a
        tie-breaker in case of an exact match among previous values.

        Note that NULL is considered smaller than any other value, so you may wish to
        filter out NULL values before sorting.

        Example usage:
        ```python
        clinical_events.sort_by(clinical_events.date, clinical_events.snomedct_code)
        ```
        """
        # Raise helpful error for easy form of mistake
        if string_arg := next((v for v in sort_values if isinstance(v, str)), None):
            raise TypeError(
                f"to sort by a column use a table attribute like "
                f"`{self.__class__.__name__}.{string_arg}` rather than the string "
                f'"{string_arg}"'
            )

        qm_node = self._qm_node
        # We expect series to be supplied highest priority first and, as the most
        # recently applied Sort operation has the highest priority, we need to apply
        # them in reverse order
        for series in reversed(sort_values):
            qm_node = _build(
                qm.Sort,
                source=qm_node,
                sort_by=_convert(series),
            )
        cls = make_sorted_event_frame_class(self.__class__)
        return cls(qm_node)


class SortedEventFrameMethods:
    def first_for_patient(self):
        """
        Return a PatientFrame containing, for each patient, the first matching row
        according to whatever sort order has been applied.

        Note that where there are multiple rows tied for first place then the specific
        row returned is picked arbitrarily but consistently i.e. you shouldn't depend on
        getting any particular result, but the result you do get shouldn't change unless
        the data changes.

        Example usage:
        ```python
        medications.sort_by(medications.date).first_for_patient()
        ```
        """
        cls = make_patient_frame_class(self.__class__)
        return cls(
            qm.PickOneRowPerPatient(
                position=qm.Position.FIRST,
                source=self._qm_node,
            )
        )

    def last_for_patient(self):
        """
        Return a PatientFrame containing, for each patient, the last matching row
        according to whatever sort order has been applied.

        Note that where there are multiple rows tied for last place then the specific
        row returned is picked arbitrarily but consistently i.e. you shouldn't depend on
        getting any particular result, but the result you do get shouldn't change unless
        the data changes.

        Example usage:
        ```python
        medications.sort_by(medications.date).last_for_patient()
        ```
        """
        cls = make_patient_frame_class(self.__class__)
        return cls(
            qm.PickOneRowPerPatient(
                position=qm.Position.LAST,
                source=self._qm_node,
            )
        )


@functools.cache
def make_sorted_event_frame_class(cls):
    """
    Given a class return a subclass which has the SortedEventFrameMethods
    """
    if issubclass(cls, SortedEventFrameMethods):
        return cls
    else:
        return type(cls.__name__, (SortedEventFrameMethods, cls), {})


@functools.cache
def make_patient_frame_class(cls):
    """
    Given an EventFrame subclass return a PatientFrame subclass with the same columns as
    the original frame
    """
    return type(
        cls.__name__,
        (PatientFrame,),
        get_all_series_and_properties_from_class(cls),
    )


def get_all_series_from_class(cls):
    # Because `Series` is a descriptor we can't access the column objects via class
    # attributes without invoking the descriptor: instead, we have to access them using
    # `vars()`. But `vars()` only gives us attributes defined directly on the class, not
    # inherited ones. So we reproduce the inheritance behaviour using `ChainMap`.
    #
    # This is _almost_ exactly what `inspect.getmembers_static` does except that returns
    # attributes in lexical order whereas we want to return the original definition
    # order.
    attrs = ChainMap(*[vars(base) for base in cls.__mro__])
    return {key: value for key, value in attrs.items() if isinstance(value, Series)}


def get_all_series_and_properties_from_class(cls):
    # Repeating the logic above but also capturing items with the @property decorator.
    # This is necessary so we can have properties as well as Series on tables. Keeping
    # the other function as there are still other uses where we just want the Series.
    attrs = ChainMap(*[vars(base) for base in cls.__mro__])
    return {
        key: value
        for key, value in attrs.items()
        if isinstance(value, Series | property)
    }


# FRAME CONSTRUCTOR ENTRYPOINTS
#


# A class decorator which replaces the class definition with an appropriately configured
# instance of the class. Obviously this is a _bit_ odd, but I think worth it overall.
# Using classes to define tables is (as far as I can tell) the only way to get nice
# autocomplete and type-checking behaviour for column names. But we don't actually want
# these classes accessible anywhere: users should only be interacting with instances of
# the classes, and having the classes themselves in the module namespaces only makes
# autocomplete more confusing and error prone.
def table[T](cls: type[T]) -> T:
    if PatientFrame in cls.__mro__:
        qm_class = qm.SelectPatientTable
    elif EventFrame in cls.__mro__:
        qm_class = qm.SelectTable
    else:
        raise Error("Schema class must subclass either `PatientFrame` or `EventFrame`")

    validate_inner_metadata_class(cls)
    try:
        table_name = cls._meta.table_name
    except AttributeError:
        table_name = cls.__name__
    try:
        required_permission = cls._meta.required_permission
    except AttributeError:
        required_permission = None

    try:
        activation_filter_field = cls._meta.activation_filter_field
    except AttributeError:
        # Default to False for tables that don't set this attribute. Some tables
        # have this field set to None to indicate that they are filtered on
        # activations, but not by a specific field.
        activation_filter_field = False

    qm_node = qm_class(
        name=table_name,
        schema=get_table_schema_from_class(cls),
        required_permission=required_permission,
        activation_filter_field=activation_filter_field,
    )
    # Register this table node with the serialization mechanism so that queries which
    # involve this table can be serialized.
    serializer_registry.register_object(qm_node, cls.__module__, cls.__qualname__)
    return cls(qm_node)


def validate_inner_metadata_class(cls):
    # Using an inner class for table metadata has advantages that make it worthwhile,
    # but it does mean that if you mistype the class name or one of the attribute names
    # then (by default) it will be silently ignored rather than throwing an error. We
    # deal with this by adding an explicit check here.
    inner_classes = {
        name
        for name, value in vars(cls).items()
        # Check whether the value looks like an inner class
        if isinstance(value, type)
        and value.__qualname__ == f"{cls.__qualname__}.{name}"
    }
    unexpected_classes = inner_classes - {"_meta"}
    if unexpected_classes:
        raise Error(
            "Expecting a single inner class called '_meta' but found: "
            f"{', '.join(unexpected_classes)}"
        )

    if "_meta" in inner_classes:
        public_attrs = {name for name in dir(cls._meta) if not name.startswith("_")}
        allowed_attrs = {"table_name", "required_permission", "activation_filter_field"}
        unexpected_attrs = public_attrs - allowed_attrs
        if unexpected_attrs:
            raise Error(
                f"Unexpected attributes on {cls.__qualname__}._meta\n"
                f"Found: {', '.join(unexpected_attrs)}\n"
                f"Allowed are: {', '.join(allowed_attrs)}"
            )


def get_table_schema_from_class(cls):
    # Get all `Series` objects on the class and determine the schema from them
    schema = {
        series.name: qm.Column(series.type_, constraints=series.constraints)
        for series in get_all_series_from_class(cls).values()
    }
    return qm.TableSchema(**schema)


# Defines a PatientFrame along with the data it contains. Takes a list (or
# any iterable) of row tuples of the form:
#
#    (patient_id, column_1_in_schema, column_2_in_schema, ...)
#
#
# This exists purely to make test cases easier to define and is not part of the public
# API.
def table_from_rows(rows):
    def decorator(cls):
        if cls.__bases__ != (PatientFrame,):
            raise Error("`@table_from_rows` can only be used with `PatientFrame`")
        qm_node = qm.InlinePatientTable(
            rows=tuple(rows),
            schema=get_table_schema_from_class(cls),
        )
        return cls(qm_node)

    return decorator


def table_from_file(path, *, columns=None):
    """
    Return a [`PatientFrame`](#PatientFrame) with data from the supplied file and having
    the specified columns. This allows you to include data extracted by other actions in
    your queries, just as if they were part of an ordinary table in the database.

    _columns_<br>
    A dictionary giving the names and types of the columns to use you want to use from
    the file. For example:
    ```python
    columns={
        "age": int,
        "sex": str,
        "index_date": datetime.date,
    }
    ```

    You don't have to include every column in the file, just the ones you want to use.
    The order of the columns doesn't matter and you don't need to include the
    `patient_id` column as ehrQL always includes this automatically.

    This feature is commonly used in [case-control studies][cc-study], where cases and
    controls are extracted and matched in separate actions and must then be combined
    together.

    For example, suppose you have a file `outputs/matched.arrow` with columns:

    patient_id | age | sex    | index_date
    ---------- | --- | ------ | ----------
    12345      |  23 | male   | 2025-06-01
    67890      |  46 | female | 2024-10-01
    …          |  …  | …      | …

    You can use this as an ehrQL table with:

    ```python
    import datetime
    from ehrql import table_from_file

    matched_patients = table_from_file(
        "outputs/matched.arrow",
        columns={
            "age": int,
            "sex": str,
            "index_date": datetime.date,
        }
    )
    ```

    You can then use `matched_patients` like any other ehrQL table e.g.
    ```python
    from ehrql import create_dataset
    from ehrql.tables.core import clinical_events

    dataset = create_dataset()
    # Include only patients with matches
    dataset.define_population(
        matched_patients.exists_for_patient()
    )

    # Find events after each matched patient's index date
    events = clinical_events.where(
        clinical_events.is_on_or_after(matched_patients.index_date)
    )
    ```

    [cc-study]: https://docs.opensafely.org/case-control-studies/
    """
    # This is backwards compatibility code. We don't really want to support the
    # decorator API and we no longer document it, but it's used by too many projects at
    # the moment to want to break compatibility here.
    if columns is None:
        return TableFromFileDecorator(path)

    schema = qm.TableSchema.from_primitives(**columns)
    column_specs = get_column_specs_from_schema(schema)
    rows = read_rows(Path(path), column_specs)
    qm_node = qm.InlinePatientTable(rows=rows, schema=schema)

    # define a subclassed PatientFrame with the relevant Series attributes
    # from provided columns
    file_table = type(
        "PatientFrameFromFile",
        (PatientFrame,),
        {name: Series(column_type) for name, column_type in columns.items()},
    )
    return file_table(qm_node)


class TableFromFileDecorator:
    def __init__(self, path):
        self._path = Path(path)

    def __call__(self, target_cls):
        if target_cls.__bases__ != (PatientFrame,):
            raise Error("`@table_from_file` can only be used with `PatientFrame`")

        schema = get_table_schema_from_class(target_cls)
        column_specs = get_column_specs_from_schema(schema)
        rows = read_rows(self._path, column_specs)
        qm_node = qm.InlinePatientTable(rows=rows, schema=schema)

        return target_cls(qm_node)

    def __getattr__(self, name):
        msg = """

        Did you forget to supply a `columns` argument to define the columns on your
        table? For example:

            my_table = table_from_file(
                "outputs/my_table.arrow",
                columns={
                    "age": int,
                    "sex": str,
                    "index_date": datetime.date,
                }
            )
        """
        exc = AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {name!r}"
        )
        exc.add_note(strip_indent(msg))
        raise exc


# A descriptor which will return the appropriate type of series depending on the type of
# frame it belongs to i.e. a PatientSeries subclass for PatientFrames and an EventSeries
# subclass for EventFrames. This lets schema authors use a consistent syntax when
# defining frames of either type.
class Series[T]:
    def __init__(
        self,
        type_: type[T],
        *,
        description="",
        constraints=(),
        required=True,
        implementation_notes_to_add_to_description="",
        notes_for_implementors="",
    ):
        self.type_ = type_
        self.description = strip_indent(description)
        self.constraints = constraints
        self.required = required
        self.implementation_notes_to_add_to_description = strip_indent(
            implementation_notes_to_add_to_description
        )
        self.notes_for_implementors = strip_indent(notes_for_implementors)

    def __set_name__(self, owner, name):
        self.name = name

    @overload
    def __get__(
        self: "Series[datetime.date]", instance: PatientFrame, owner
    ) -> "DatePatientSeries": ...

    @overload
    def __get__(
        self: "Series[datetime.date]", instance: EventFrame, owner
    ) -> DateEventSeries: ...

    @overload
    def __get__(
        self: "Series[CodeT]", instance: PatientFrame, owner
    ) -> CodePatientSeries: ...

    @overload
    def __get__(
        self: "Series[CodeT]", instance: EventFrame, owner
    ) -> CodeEventSeries: ...

    @overload
    def __get__(
        self: "Series[MultiCodeStringT]", instance: PatientFrame, owner
    ) -> MultiCodeStringPatientSeries: ...

    @overload
    def __get__(
        self: "Series[MultiCodeStringT]", instance: EventFrame, owner
    ) -> MultiCodeStringEventSeries: ...

    @overload
    def __get__(
        self: "Series[bool]", instance: PatientFrame, owner
    ) -> BoolPatientSeries: ...

    @overload
    def __get__(
        self: "Series[bool]", instance: EventFrame, owner
    ) -> BoolEventSeries: ...

    @overload
    def __get__(
        self: "Series[str]", instance: PatientFrame, owner
    ) -> StrPatientSeries: ...

    @overload
    def __get__(
        self: "Series[str]", instance: EventFrame, owner
    ) -> "StrEventSeries": ...

    @overload
    def __get__(
        self: "Series[int]", instance: PatientFrame, owner
    ) -> IntPatientSeries: ...

    @overload
    def __get__(self: "Series[int]", instance: EventFrame, owner) -> IntEventSeries: ...

    @overload
    def __get__(
        self: "Series[float]", instance: PatientFrame, owner
    ) -> FloatPatientSeries: ...

    @overload
    def __get__(
        self: "Series[float]", instance: EventFrame, owner
    ) -> FloatEventSeries: ...

    def __get__(self, instance, owner):
        if instance is None:  # pragma: no cover
            return self
        return instance._select_column(self.name)


def get_tables_from_namespace(namespace):
    """
    Yield all ehrQL tables contained in `namespace`
    """
    for attr, value in vars(namespace).items():
        if isinstance(value, BaseFrame):
            yield attr, value


# CASE EXPRESSION FUNCTIONS
#


class when:
    def __init__(self, condition):
        condition_qm = _convert(condition)
        type_ = get_series_type(condition_qm)
        if type_ is not bool:
            raise TypeError(
                f"invalid case condition:\n"
                f"Expecting a boolean series, got series of type"
                f" '{type_.__qualname__}'",
            )
        self._condition = condition_qm

    def then(self, value):
        return WhenThen(self._condition, _convert(value))


class WhenThen:
    def __init__(self, condition, value):
        self._condition = condition
        self._value = value

    def otherwise(self, value):
        return case(self, otherwise=value)


def case(*when_thens, otherwise=None):
    """
    Take a sequence of condition-values of the form:
    ```python
    when(condition).then(value)
    ```

    And evaluate them in order, returning the value of the first condition which
    evaluates True. If no condition matches, return the `otherwise` value (or NULL
    if no `otherwise` value is specified).

    Example usage:
    ```python
    category = case(
        when(size < 10).then("small"),
        when(size < 20).then("medium"),
        when(size >= 20).then("large"),
        otherwise="unknown",
    )
    ```

    Note that because the conditions are evaluated in order we don't need the condition
    for "medium" to specify `(size >= 10) & (size < 20)` because by the time the
    condition for "medium" is being evaluated we already know the condition for "small"
    is False.

    A simpler form is available when there is a single condition.  This example:
    ```python
    category = case(
        when(size < 15).then("small"),
        otherwise="large",
    )
    ```

    can be rewritten as:
    ```python
    category = when(size < 15).then("small").otherwise("large")
    ```
    """
    cases = {}
    for case in when_thens:
        if isinstance(case, when):
            raise TypeError(
                "`when(...)` clause missing a `.then(...)` value in `case()` expression"
            )
        elif (
            isinstance(case, BaseSeries)
            and isinstance(case._qm_node, qm.Case)
            and len(case._qm_node.cases) == 1
        ):
            raise TypeError(
                "invalid syntax for `otherwise` in `case()` expression, instead of:\n"
                "\n"
                "    case(\n"
                "        when(...).then(...).otherwise(...)\n"
                "    )\n"
                "\n"
                "You should write:\n"
                "\n"
                "    case(\n"
                "        when(...).then(...),\n"
                "        otherwise=...\n"
                "    )\n"
                "\n"
            )
        elif not isinstance(case, WhenThen):
            raise TypeError(
                "cases must be specified in the form:\n"
                "\n"
                "    when(<CONDITION>).then(<VALUE>)\n"
                "\n"
            )
        elif case._condition in cases:
            raise TypeError("duplicated condition in `case()` expression")
        else:
            cases[case._condition] = case._value
    if not cases:
        raise TypeError("`case()` expression requires at least one case")
    if otherwise is None and all(value is None for value in cases.values()):
        raise TypeError("`case()` expression cannot have all `None` values")
    return _wrap(qm.Case, cases, default=_convert(otherwise))


# HORIZONTAL AGGREGATION FUNCTIONS
#
# These cast all arguments to the first Series. So if we have a Series as
# the first arg then we know the return type. However, if the first arg is
# not a Series, then we don't know the return type. E.g. the following examples
# are tricky:
# maximum_of(10, 10, clinical_events.numeric_value) - will return FloatEventSeries
# maximum_of("2024-01-01", "2023-01-01", clinical_events.date) - will return DateEventSeries
@overload
def maximum_of[IntT: "IntFunctions"](
    value: IntT, other_value, *other_values
) -> IntT: ...
@overload
def maximum_of[FloatT: "FloatFunctions"](
    value: FloatT, other_value, *other_values
) -> FloatT: ...
@overload
def maximum_of[DateT: "DateFunctions"](
    value: DateT, other_value, *other_values
) -> DateT: ...
def maximum_of(value, other_value, *other_values) -> int:
    """
    Return the maximum value of a collection of Series or Values, disregarding NULLs.
    Unless all values in the collection are NULL, in which case return NULL.

    Example usage:
    ```python
    latest_event_date = maximum_of(event_series_1.date, event_series_2.date, "2001-01-01")
    ```
    """
    args = cast_all_arguments((value, other_value, *other_values))
    return _apply(qm.Function.MaximumOf, args)


@overload
def minimum_of[IntT: "IntFunctions"](
    value: IntT, other_value, *other_values
) -> IntT: ...
@overload
def minimum_of[FloatT: "FloatFunctions"](
    value: FloatT, other_value, *other_values
) -> FloatT: ...
@overload
def minimum_of[DateT: "DateFunctions"](
    value: DateT, other_value, *other_values
) -> DateT: ...
def minimum_of(value, other_value, *other_values):
    """
    Return the minimum value of a collection of Series or Values, disregarding NULLs.
    Unless all values in the collection are NULL, in which case return NULL.

    Example usage:
    ```python
    earliest_event_date = minimum_of(event_series_1.date, event_series_2.date, "2001-01-01")
    ```
    """
    args = cast_all_arguments((value, other_value, *other_values))
    return _apply(qm.Function.MinimumOf, args)


# ERROR HANDLING
#


def raise_helpful_error_if_possible(arg):
    if isinstance(arg, BaseFrame):
        raise TypeError(
            f"Expecting a series but got a frame (`{arg.__class__.__name__}`): "
            f"are you missing a column name?"
        )
    if callable(arg):
        raise TypeError(
            f"Function referenced but not called: are you missing parentheses on "
            f"`{arg.__name__}()`?"
        )
    if isinstance(arg, when):
        raise TypeError(
            "Missing `.then(...).otherwise(...)` conditions on a `when(...)` expression"
        )
    if isinstance(arg, WhenThen):
        raise TypeError(
            "Missing `.otherwise(...)` condition on a `when(...).then(...)` expression\n"
            "Note: you can use `.otherwise(None)` to get NULL values"
        )


def validate_ehrql_series(arg, context):
    try:
        raise_helpful_error_if_possible(arg)
    except TypeError as e:
        raise TypeError(f"invalid {context}:\n{e})") from None
    if not isinstance(arg, BaseSeries):
        exc = TypeError(
            f"invalid {context}:\n"
            f"Expecting an ehrQL series, got type '{type(arg).__qualname__}'"
        )
        # If we get a series wrapped in a single-member tuple then probably this is a
        # trailing comma error
        if isinstance(arg, tuple) and len(arg) == 1 and isinstance(arg[0], BaseSeries):
            exc.add_note(TRAILING_COMMA_HINT)
        raise exc


def validate_patient_series(arg, context):
    validate_ehrql_series(arg, context)
    if not isinstance(arg, PatientSeries):
        raise TypeError(
            f"invalid {context}:\nExpecting a series with only one value per patient"
        )


def validate_patient_series_type(arg, types, context):
    validate_patient_series(arg, context)
    if arg._type not in types:
        types_desc = humanize_list_of_types(types)
        article = "an" if types_desc[0] in "aeiou" else "a"
        raise TypeError(
            f"invalid {context}:\n"
            f"Expecting {article} {types_desc} series, got series of type"
            f" '{arg._type.__qualname__}'",
        )


HUMAN_TYPES = {
    bool: "boolean",
    int: "integer",
}


def humanize_list_of_types(types):
    type_names = [HUMAN_TYPES.get(type_, type_.__qualname__) for type_ in types]
    initial = ", ".join(type_names[:-1])
    return f"{initial} or {type_names[-1]}" if initial else type_names[-1]


def modify_exception(exc):
    # This is our chance to modify exceptions which we didn't raise ourselves to make
    # them more helpful or add additional context
    if operator := _get_operator_error(exc):
        exc.add_note(
            _format_operator_error_note(operator),
        )
    return exc


def _get_operator_error(exc):
    # Because `and`, `or` and `not` are control-flow primitives in Python they are not
    # overridable and so we're forced to use the bitwise operators for logical
    # operations. However these have different precedence rules from those governing the
    # standard operators and so it's easy to accidentally do the wrong thing. Here we
    # identify errors associated with the logical operators so we can add a note trying
    # to explain what might have happened.
    if not isinstance(exc, TypeError):
        return
    # Sadly we have to do this via string matching on the exception text
    if match := re.match(
        r"(unsupported operand type\(s\) for|bad operand type for unary) ([|&~]):",
        str(exc),
    ):
        return match.group(2)


def _format_operator_error_note(operator):
    if operator == "|":
        example_bad = "a == b | x == y"
        example_good = "(a == b) | (x == y)"
    elif operator == "&":
        example_bad = "a == b & x == y"
        example_good = "(a == b) & (x == y)"
    elif operator == "~":
        example_bad = "~ a == b"
        example_good = "~ (a == b)"
    else:
        assert False
    return (
        f"\n"
        f"WARNING: The `{operator}` operator has surprising precedence rules, meaning\n"
        "you may need to add more parentheses to get the correct behaviour.\n"
        f"\n"
        f"For example, instead of writing:\n"
        f"\n"
        f"    {example_bad}\n"
        f"\n"
        f"You should write:\n"
        f"\n"
        f"    {example_good}"
    )
