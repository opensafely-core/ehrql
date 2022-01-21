"""This module provides classes for building a cohort using the DSL.

Database tables are modelled by PatientFrame (a collection of records with one record
per patient) and EventFrame (a collection of records with multiple records per patient).

Through filtering, sorting, aggregating, and selecting columns, we transform instances
of PatientFrame/EventFrame into instances of PatientSeries.

A PatientSeries represents a mapping from a patient to a value, and can be assigned to a
Cohort.  In the future, a PatientSeries will be able to be combined with another
PatientSeries or a single value to produce a new PatientSeries.

All classes except Cohort are intended to be immutable.

Methods are designed so that users can only perform actions that are semantically
meaningful.  This means that the order of operations is restricted.  In a terrible ASCII
railway diagram:

             +---+
             |   V
      filter |  EventFrame -----------------------+
             |   |   |                            |
             +---+   | sort_by                    |
                     V                            |
             SortedEventFrame                     |
                     |                            |
                     | (first/last)_for_patient   | (count/exists)_for_patient
                     V                            |
                PatientFrame                      |
                     |                            |
                     | select_column              |
                     V                            |
          +--> PatientSeries <--------------------+
  round_X |          |
          +----------+

To support providing helpful error messages, we can implement __getattr__ on each class.
This will intercept any lookup of a missing attribute, so that if eg a user tries to
select a column from a SortedEventFrame, we can tell them they need to aggregate the
SortedEventFrame first_for_patient.

This docstring, and the function docstrings in this module are not currently intended
for end users.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar, overload

from .query_model import (
    DEFAULT_JOIN_COLUMN,
    Aggregate,
    AggregationFunction,
    ApplyFunction,
    Categorise,
    Codelist,
    ColumnValue,
    Filter,
    Function,
    SelectColumn,
    SelectTable,
    SortAndSelectFirst,
    TableValue,
)


class Cohort:
    """
    Represents the cohort of patients in the defined study.
    """

    def set_population(self, population: PatientSeries) -> None:
        """
        Sets the population that are included within the Cohort.

        Args:
            population: A boolean series indicating if any given patient
                are included within the Cohort
        """

        self.population = population
        value = population.value

        if not (
            isinstance(value, Aggregate)
            and value.function == AggregationFunction.EXISTS
        ):
            raise ValueError(
                "Population variable must return a boolean. Did you mean to use `exists_for_patient()`?"
            )

    def add_variable(self, name: str, variable: PatientSeries) -> None:
        """
        Add a variable to this Cohort with a given name.

        Args:
            name: The name of the variable to add
            variable: The PatientSeries to add as the named variable.
        """

        self.__setattr__(name, variable)

    def __setattr__(self, name: str, variable: PatientSeries) -> None:
        if not isinstance(variable, PatientSeries):
            raise TypeError(
                f"{name} must be a single value per patient (got '{variable.__class__.__name__}')"
            )
        super().__setattr__(name, variable)


class EventFrame:
    """
    An EventFrame is a representation of an unsorted collection of patient records.
    Patients can have multiple rows within the EventFrame and operations such as
    filter() can be run over the EventFrame to produce new Frames.
    """

    def __init__(self, qm_table: TableValue):
        """
        Initialise the EventFrame

        Args:
            qm_table: A Table in a given backend that this EventFrame is generated
            from.
        """
        self.qm_table = qm_table

    def filter(self, predicate: Predicate | BoolColumn) -> EventFrame:  # noqa: A003
        """
        Filters the EventFrame with a given filter, and returns a
        new Event Frame.

        Args:
            predicate: The Definition of the filter that this EventFrame is being
                filtered by.

        Returns:
              EventFrame: A new EventFrame that is filtered by the conditions
        """
        if isinstance(predicate, BoolColumn):
            predicate = predicate.is_true()

        return EventFrame(predicate.apply_to(self.qm_table))

    def sort_by(self, *columns: Column[S]) -> SortedEventFrame:
        """
        Sorts an EventFrame by a specific column, such as a date column, and
        returns a SortedEventFrame with a given sort column.

        Args:
            columns: Name of the column you wish to sort by

        Returns:
            SortedEventFrame with a given sort column
        """
        return SortedEventFrame(self.qm_table, *columns)

    def count_for_patient(self) -> IntSeries:
        """
        Takes the information from the multiple row per patient EventFrame and counts
        the events per patient.

        Args:
            None

        Returns:
            IntSeries: A count of events per patient
        """
        return IntSeries(
            self._apply_aggregation(self.qm_table, AggregationFunction.COUNT)
        )

    def exists_for_patient(self) -> BoolSeries:
        """
        Takes the information from the multiple row per patient EventFrame and returns a Boolean
        indicating if the Patient has a matching event.

        Args:
            None

        Returns:
            BoolSeries: A BoolSeries indicating whether each patient has a matching event.
        """
        return BoolSeries(
            self._apply_aggregation(self.qm_table, AggregationFunction.EXISTS)
        )

    @staticmethod
    def _apply_aggregation(qm_table, function):
        return Aggregate(
            function,
            (SelectColumn(qm_table, DEFAULT_JOIN_COLUMN),),
        )


class EventTable(EventFrame):
    def __init__(self, contract):
        contract.validate_frame(type(self))
        qm_table = SelectTable(contract._name)
        super().__init__(qm_table)


class SortedEventFrame:
    """
    An SortedEventFrame is a representation of sorted collection of patient records.
    Patients can have multiple rows within the SortedEventFrame and operations such as
    filter() can be run over the SortedEventFrame to produce new Frames.
    """

    def __init__(self, qm_table: TableValue, *sort_columns: Column[S]):
        """
        Initialise the SortedEventFrame

        Args:
            qm_table: A Table in a given backend that this SortedEventFrame is generated
            from.
            sort_columns: The Columns of the SortedEventFrame that it is sorted by.
        """
        self.qm_table = qm_table
        self.sort_columns = sort_columns

    def first_for_patient(self) -> PatientFrame:
        """
        Return a PatientFrame with the first event for each patient. Each patient
        can have a maximum of one row in the PatientFrame.
        """
        return self._sort_and_select(descending=False)

    def last_for_patient(self) -> PatientFrame:
        """
        Return a PatientFrame with the last event for each patient. Each patient
        can have a maximum of one row in the PatientFrame.
        """
        return self._sort_and_select(descending=True)

    def _sort_and_select(self, descending):
        sort_columns = tuple(
            SelectColumn(self.qm_table, c.name) for c in self.sort_columns
        )
        return PatientFrame(
            row=SortAndSelectFirst(self.qm_table, sort_columns, descending=descending)
        )


class PatientFrame:
    """
    Represents an unsorted collection of records, with one row per patient.
    """

    def __init__(self, row: SortAndSelectFirst):
        """
        Initialise the PatientFrame

        Args:
            row: A Row which represents a single patient's data
        """
        self.row = row

    def select_column(self, column: Column[S]) -> S:
        """
        Return a PatientSeries containing given column.

        Args:
            column: The Column of interest of which you want to retrieve the value.
        """
        return column.series_type(SelectColumn(self.row, column.name))


class PatientTable(PatientFrame):
    def __init__(self, contract):
        contract.validate_frame(type(self))
        qm_table = SelectTable(contract._name)
        # TODO: revisit this!  As things stand, this will generate SQL with an
        # unnecessary PARTITION OVER, which may carry a performance penalty.
        row = SortAndSelectFirst(
            qm_table, (SelectColumn(qm_table, DEFAULT_JOIN_COLUMN),)
        )
        super().__init__(row)


class PatientSeries:
    """
    Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """

    def __init__(self, value: ColumnValue):
        self.value = value

    def __eq__(self, other: PatientSeries | str | int) -> BoolSeries:  # type: ignore[override]
        # All python objects have __eq__ and __ne__ defined, so overriding these methods
        # involves overriding them on a superclass (`object`), which results in
        # a typing error as it violates the violates the Liskov substitution principle
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        # We are deliberately overloading the operators here, hence the ignore
        other_value = other.value if isinstance(other, PatientSeries) else other
        return BoolSeries(value=ApplyFunction(Function.EQ, (self.value, other_value)))

    def __ne__(self, other: PatientSeries | str | int) -> BoolSeries:  # type: ignore[override]
        other_value = other.value if isinstance(other, PatientSeries) else other
        return BoolSeries(value=ApplyFunction(Function.NE, (self.value, other_value)))

    def __hash__(self) -> int:
        return hash(repr(self.value))

    def __invert__(self) -> PatientSeries:
        return PatientSeries(value=ApplyFunction(Function.NOT, (self.value,)))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class BoolSeries(PatientSeries):
    def __and__(self, other: BoolSeries) -> BoolSeries:
        return BoolSeries(value=ApplyFunction(Function.AND, (self.value, other.value)))

    def __or__(self, other: BoolSeries) -> BoolSeries:
        return BoolSeries(value=ApplyFunction(Function.OR, (self.value, other.value)))


class CodeSeries(PatientSeries):
    def __and__(self, other: CodeSeries) -> BoolSeries:
        return BoolSeries(value=ApplyFunction(Function.AND, (self.value, other.value)))

    def __invert__(self) -> BoolSeries:
        return BoolSeries(value=ApplyFunction(Function.NOT, (self.value,)))


def _validate_datestring(datestring):
    try:
        datetime.strptime(datestring, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(
            f"{datestring} is not a valid date; date must in YYYY-MM-DD format"
        )
    return datestring


def is_function(value, function):
    if not isinstance(value, ApplyFunction):
        return False
    return value.function == function


class DateSeries(PatientSeries):
    @staticmethod
    def _get_other_date_value(other):
        return (
            other.value
            if isinstance(other, DateSeries)
            else _validate_datestring(other)
        )

    def _apply_fn(self, fn, other):
        return BoolSeries(
            value=ApplyFunction(fn, (self.value, self._get_other_date_value(other)))
        )

    def __gt__(self, other: DateSeries | str) -> BoolSeries:
        return self._apply_fn(Function.GT, other)

    def __ge__(self, other: DateSeries | str) -> BoolSeries:
        return self._apply_fn(Function.GE, other)

    def __lt__(self, other: DateSeries | str) -> BoolSeries:
        return self._apply_fn(Function.LT, other)

    def __le__(self, other: DateSeries | str) -> BoolSeries:
        return self._apply_fn(Function.LE, other)

    def __ne__(self, other: DateSeries | str) -> BoolSeries:  # type: ignore[override]
        return self._apply_fn(Function.NE, other)

    def round_to_first_of_month(self) -> DateSeries:
        return DateSeries(
            ApplyFunction(Function.ROUND_TO_FIRST_OF_MONTH, (self.value,))
        )

    def round_to_first_of_year(self) -> DateSeries:
        return DateSeries(ApplyFunction(Function.ROUND_TO_FIRST_OF_YEAR, (self.value,)))

    @staticmethod
    def _get_other_datedelta_value(delta_value, operation):
        """Ensure we have either a simple int, or an IntSeries representing a date difference in days"""
        if isinstance(delta_value, DateDeltaSeries) and is_function(
            delta_value.value, Function.DATE_DIFFERENCE
        ):
            return delta_value.convert_to_days().value
        elif isinstance(delta_value, int):
            return delta_value
        else:
            raise ValueError(
                f"Can only {operation} integer or DateDeltaSeries (got <{delta_value.__class__.__name__}>)"
            )

    def __sub__(
        self, other: str | DateSeries | DateDeltaSeries | IntSeries | int
    ) -> DateDeltaSeries | DateSeries:
        if isinstance(other, (str, DateSeries)):
            return DateDeltaSeries(
                ApplyFunction(
                    Function.DATE_DIFFERENCE,
                    (self._get_other_date_value(other), self.value),
                )
            )
        other_value = self._get_other_datedelta_value(other, "subtract")
        return DateSeries(
            ApplyFunction(Function.DATE_SUBTRACT, (self.value, other_value))
        )

    def __rsub__(self, other: str | DateSeries) -> DateDeltaSeries:
        # consistent with python datetime/timedelta, we cannot subtract a DateSeries from
        # anything other than a date or another DateSeries
        try:
            return DateDeltaSeries(
                ApplyFunction(
                    Function.DATE_DIFFERENCE,
                    (self.value, self._get_other_date_value(other)),
                )
            )
        except ValueError:
            if isinstance(other, str):
                raise
            raise TypeError(
                f"Can't subtract DateSeries from {other.__class__.__name__}"
            )

    def __add__(self, other: DateDeltaSeries | int) -> DateSeries:
        other_value = self._get_other_datedelta_value(other, "add")
        return DateSeries(ApplyFunction(Function.DATE_ADD, (self.value, other_value)))

    def __radd__(self, other: int) -> DateSeries:
        # Note that other cannot be a DateDeltaSeries, as this is handled by DateDeltaSeries.__add__
        return self + other


class DateDeltaSeries(PatientSeries):
    def _convert(self, units):
        if not is_function(self.value, Function.DATE_DIFFERENCE):
            raise ValueError("Can only convert differences between dates")
        start_date, end_date = self.value.arguments[:2]
        return IntSeries(
            ApplyFunction(Function.DATE_DIFFERENCE, (start_date, end_date, units))
        )

    def convert_to_years(self):
        return self._convert("years")

    def convert_to_months(self):
        return self._convert("months")

    def convert_to_days(self):
        return self._convert("days")

    def convert_to_weeks(self):
        return self._convert("weeks")

    @staticmethod
    def _delta_in_days(datedelta):
        """
        Convert a DateSeltaSeries representing the difference between two dates to an
        IntSeries representing days.
        """
        if isinstance(datedelta, DateDeltaSeries):
            if is_function(datedelta.value, Function.DATE_DIFFERENCE):
                return datedelta.convert_to_days().value
            else:
                return datedelta.value
        return datedelta

    def __add__(
        self, other: DateDeltaSeries | DateSeries | int
    ) -> DateDeltaSeries | DateSeries:
        # Adding a DateSeries to a DateDeltaSeries should use DateSeries.__add__ to
        # return a new DateSeries
        if isinstance(other, DateSeries):
            return other + self
        return DateDeltaSeries(
            ApplyFunction(
                Function.DATE_DELTA_ADD,
                (self._delta_in_days(self), self._delta_in_days(other)),
            )
        )

    def __radd__(self, other: int) -> DateDeltaSeries | DateSeries:
        # Note that other cannot be a DateSeries, as this is handled by DateSeries.__add__
        return self + other

    def __sub__(self, other: DateDeltaSeries | int) -> DateDeltaSeries:
        return DateDeltaSeries(
            ApplyFunction(
                Function.DATE_DELTA_SUBTRACT,
                (self._delta_in_days(self), self._delta_in_days(other)),
            )
        )

    def __rsub__(
        self, other: str | DateDeltaSeries | int
    ) -> DateSeries | DateDeltaSeries:
        # Note that other cannot be a DateSeries, as this is handled by DateSeries.__sub__
        if isinstance(other, str):
            datestring = _validate_datestring(other)
            # This allows subtraction of a DateDeltaSeries from a date string
            # e.g. 2020-10-01
            return DateSeries(
                ApplyFunction(
                    Function.DATE_SUBTRACT,
                    (datestring, self.convert_to_days().value),
                )
            )
        return DateDeltaSeries(
            ApplyFunction(
                Function.DATE_DELTA_SUBTRACT,
                (self._delta_in_days(other), self._delta_in_days(self)),
            )
        )


class IdSeries(PatientSeries):
    pass


class IntSeries(PatientSeries):
    def _apply_fn(self, fn, other):
        other_value = other.value if isinstance(other, IntSeries) else other
        return BoolSeries(value=ApplyFunction(fn, (self.value, other_value)))

    def __gt__(self, other: IntSeries | int) -> BoolSeries:
        return self._apply_fn(Function.GT, other)

    def __ge__(self, other: IntSeries | int) -> BoolSeries:
        return self._apply_fn(Function.GE, other)

    def __lt__(self, other: IntSeries | int) -> BoolSeries:
        return self._apply_fn(Function.LT, other)

    def __le__(self, other: IntSeries | int) -> BoolSeries:
        return self._apply_fn(Function.LE, other)

    def __ne__(self, other: IntSeries | int) -> BoolSeries:  # type: ignore[override]
        return self._apply_fn(Function.NE, other)


class FloatSeries(PatientSeries):
    pass


class StrSeries(PatientSeries):
    pass


S = TypeVar("S", bound=PatientSeries)


class Predicate:
    def __init__(
        self,
        column: Column[S],
        operator: Function,
        other: str | bool | int | Codelist | None,
    ) -> None:
        self._column = column
        self._operator = operator
        self._other = other

    def apply_to(self, table: TableValue) -> TableValue:
        column = SelectColumn(table, self._column.name)
        condition = ApplyFunction(self._operator, (column, self._other))
        return Filter(table, condition)


@dataclass
class Column(Generic[S]):
    name: str
    series_type: type[S]

    def is_not_null(self):
        return Predicate(self, Function.NE, None)


class IdColumn(Column[IdSeries]):
    def __init__(self, name):
        super().__init__(name, IdSeries)


class BoolColumn(Column[BoolSeries]):
    def __init__(self, name):
        super().__init__(name, BoolSeries)

    def is_true(self) -> Predicate:
        return Predicate(self, Function.EQ, True)

    def is_false(self) -> Predicate:
        return Predicate(self, Function.EQ, False)

    def __eq__(self, other: bool) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        if other:
            return self.is_true()
        else:
            return self.is_false()

    def __ne__(self, other: bool) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        if other:
            return self.is_false()
        else:
            return self.is_true()


class DateColumn(Column[DateSeries]):
    def __init__(self, name):
        super().__init__(name, DateSeries)

    def __eq__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, Function.EQ, other)

    def __ne__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, Function.NE, other)

    def __gt__(self, other: str) -> Predicate:
        return Predicate(self, Function.GT, other)

    def __ge__(self, other: str) -> Predicate:
        return Predicate(self, Function.GE, other)

    def __lt__(self, other: str) -> Predicate:
        return Predicate(self, Function.LT, other)

    def __le__(self, other: str) -> Predicate:
        return Predicate(self, Function.LE, other)


class CodeColumn(Column[CodeSeries]):
    def __init__(self, name):
        super().__init__(name, CodeSeries)

    def __eq__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, Function.EQ, other)

    def __ne__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, Function.NE, other)

    def is_in(self, codelist: Codelist) -> Predicate:
        if isinstance(codelist, list):
            codelist = tuple(codelist)
        return Predicate(self, Function.IN, codelist)


class IntColumn(Column[IntSeries]):
    def __init__(self, name):
        super().__init__(name, IntSeries)

    def __eq__(self, other: int) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, Function.EQ, other)

    def __ne__(self, other: int) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, Function.NE, other)

    def __gt__(self, other: int) -> Predicate:
        return Predicate(self, Function.GT, other)

    def __ge__(self, other: int) -> Predicate:
        return Predicate(self, Function.GE, other)

    def __lt__(self, other: int) -> Predicate:
        return Predicate(self, Function.LT, other)

    def __le__(self, other: int) -> Predicate:
        return Predicate(self, Function.LE, other)


class FloatColumn(Column[FloatSeries]):
    def __init__(self, name):
        super().__init__(name, FloatSeries)


class StrColumn(Column[StrSeries]):
    def __init__(self, name):
        super().__init__(name, StrSeries)


def not_null_patient_series(patient_series: PatientSeries) -> PatientSeries:
    """
    Generates a new PatientSeries where all null values are removed.

    Args:
        patient_series: PatientSeries that may contain null values

    Returns:
        PatientSeries: A new PatientsSeries without null values
    """
    is_not_null = ApplyFunction(Function.NE, (patient_series.value, None))
    return PatientSeries(value=is_not_null)


T = TypeVar("T", str, int)


@overload
def categorise(mapping: dict[str, PatientSeries], default: str | None) -> PatientSeries:
    ...


@overload
def categorise(mapping: dict[int, PatientSeries], default: int | None) -> PatientSeries:
    ...


def categorise(mapping, default=None):
    """
    Represents a switch statement.

    mapping: A dict mapping category keys to category expressions, e.g.
        {
            "0-17": age < 18,
            "18-24": (age >= 18) & (age < 25),
            "25-34": (age >= 25) & (age < 35),
            "35-44": (age >= 35) & (age < 45),
            "45-54": (age >= 45) & (age < 55),
            "55-69": (age >= 55) & (age < 70),
            "70-79": (age >= 70) & (age < 80),
            "80+": age >= 80,
        }
        where `age` is a PatientSeries
        Category expressions can be Comparators generated by comparing a PatientSeries
        with a constant, as above, or simple PatientSeries (which will be converted to a
        not-null comparison)
        {
            "has_code": code,
        }
        where `code` is a PatientSeries, selecting the column "code"

    returns: PatientSeries with a ValueFromCategory value
    """
    _validate_category_mapping(mapping, default)
    value_mapping = {
        key: patient_series.value
        if isinstance(patient_series, BoolSeries)
        else not_null_patient_series(patient_series).value
        for key, patient_series in mapping.items()
    }
    return PatientSeries(value=Categorise(value_mapping, default))


# Typed as object because the alternative is another overloaded function here which is unnecessary ceremony for this
# internal function.
def _validate_category_mapping(
    mapping: dict[object, PatientSeries], default: object
) -> None:
    """
    Ensure that a category mapping is valid.

    It does this by checking that:
    - there are no duplicate values
    - all keys are the same type
    - all values are PatientSeries
    - default value is None, or the same type as the keys

    Args:
        mapping: A key-value pair of an Expression and the resultant PatientSeries
        default: Default values
    """
    errors: list[Exception] = []
    duplicates = set()
    seen_values = set()
    key_types = set()
    for key, mapping_value in mapping.items():
        key_types.add(type(key))
        if not isinstance(mapping_value, PatientSeries):
            #  Although this is unreachable is the type annotation is enforced, we still want
            # to check for it at runtime
            errors.append(  # type: ignore[unreachable]
                TypeError(
                    "Category values must be either a PatientSeries, "
                    "or a comparison expression involving a PatientSeries. "
                    f"Got '{mapping_value}' ({type(mapping_value)}) for category key '{key}'"
                )
            )
        if mapping_value in seen_values and key not in duplicates:
            duplicates.add(key)
            errors.append(
                ValueError(f"Duplicate category values found for key: '{key}'")
            )
        seen_values.add(mapping_value)

    if len(key_types) > 1:
        errors.append(
            TypeError(
                f"Multiple category key types found: {', '.join([f'{str(key)} ({type(key)})' for key in mapping.keys()])}"
            )
        )
    else:
        # If there is more than one key type, we can't tell what the default should be, so
        # defer validation until we have a single key type to check against
        key_type = key_types.pop()
        if default is not None and type(default) != key_type:
            errors.append(
                TypeError(
                    f"Default category must be None, or the same type as mapped categories (expected {key_type}, got {type(default)})"
                )
            )

    raise_category_errors(errors)


def raise_category_errors(errors):
    """Recursively raise any category errors found."""
    if not errors:
        return
    try:
        next_category_error = errors.pop()
        raise next_category_error
    finally:
        raise_category_errors(errors)
