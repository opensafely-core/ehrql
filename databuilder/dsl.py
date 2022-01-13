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
    BaseTable,
    Codelist,
    Comparator,
    DateAddition,
    DateDeltaAddition,
    DateDeltaSubtraction,
    DateDifference,
    DateSubtraction,
    RoundToFirstOfMonth,
    RoundToFirstOfYear,
    Row,
    Table,
    Value,
    ValueFromAggregate,
    ValueFromCategory,
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
            isinstance(value, ValueFromAggregate) and value.source.function == "exists"
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

    def __init__(self, qm_table: BaseTable):
        """
        Initialise the EventFrame

        Args:
            qm_table: A Table in a given backend that this EventFrame is generated
            from.
        """
        self.qm_table = qm_table

    @classmethod
    def from_contract(cls, contract):
        contract.validate_frame(cls)
        qm_table = Table(contract._name)
        return cls(qm_table)

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
        return IntSeries(self.qm_table.count())

    def exists_for_patient(self) -> BoolSeries:
        """
        Takes the information from the multiple row per patient EventFrame and returns a Boolean
        indicating if the Patient has a matching event.

        Args:
            None

        Returns:
            BoolSeries: A BoolSeries indicating whether each patient has a matching event.
        """
        return BoolSeries(self.qm_table.exists())


class SortedEventFrame:
    """
    An SortedEventFrame is a representation of sorted collection of patient records.
    Patients can have multiple rows within the SortedEventFrame and operations such as
    filter() can be run over the SortedEventFrame to produce new Frames.
    """

    def __init__(self, qm_table: BaseTable, *sort_columns: Column[S]):
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
        return PatientFrame(row=self.qm_table.first_by(*self._sort_column_names()))

    def last_for_patient(self) -> PatientFrame:
        """
        Return a PatientFrame with the last event for each patient. Each patient
        can have a maximum of one row in the PatientFrame.
        """
        return PatientFrame(row=self.qm_table.last_by(*self._sort_column_names()))

    def _sort_column_names(self):
        return [c.name for c in self.sort_columns]


class PatientFrame:
    """
    Represents an unsorted collection of records, with one row per patient.
    """

    def __init__(self, row: Row):
        """
        Initialise the PatientFrame

        Args:
            row: A Row which represents a single patient's data
        """
        self.row = row

    @classmethod
    def from_contract(cls, contract):
        contract.validate_frame(cls)
        qm_table = Table(contract._name)
        # TODO: revisit this!  As things stand, this will generate SQL with an
        # unnecessary PARTITION OVER, which may carry a performance penalty.
        return cls(qm_table.first_by("patient_id"))

    def select_column(self, column: Column[S]) -> S:
        """
        Return a PatientSeries containing given column.

        Args:
            column: The Column of interest of which you want to retrieve the value.
        """
        return column.series_type(self.row.get(column.name))


class PatientSeries:
    """
    Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """

    def __init__(self, value: Value | Comparator):
        self.value = value

    def _is_comparator(self) -> bool:
        return isinstance(self.value, Comparator)

    def __eq__(self, other: PatientSeries | Comparator | str | int) -> BoolSeries:  # type: ignore[override]
        # All python objects have __eq__ and __ne__ defined, so overriding these methods
        # involves overriding them on a superclass (`object`), which results in
        # a typing error as it violates the violates the Liskov substitution principle
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        # We are deliberately overloading the operators here, hence the ignore
        other_value = other.value if isinstance(other, PatientSeries) else other
        return BoolSeries(value=self.value == other_value)

    def __ne__(self, other: PatientSeries | Comparator | str | int) -> BoolSeries:  # type: ignore[override]
        return BoolSeries(value=self.value != other)

    def __hash__(self) -> int:
        return hash(repr(self.value))

    def __invert__(self) -> PatientSeries:
        if self._is_comparator():
            comparator_value = ~self.value
        else:
            comparator_value = Comparator(
                lhs=self.value, operator="__ne__", rhs=None, negated=True
            )
        return PatientSeries(value=comparator_value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"


class BoolSeries(PatientSeries):
    def __and__(self, other: BoolSeries) -> BoolSeries:
        return BoolSeries(value=self.value & other.value)

    def __or__(self, other: BoolSeries) -> BoolSeries:
        return BoolSeries(value=self.value | other.value)


class CodeSeries(PatientSeries):
    def __and__(self, other: CodeSeries) -> BoolSeries:
        return BoolSeries(value=self.value & other.value)

    def __invert__(self) -> BoolSeries:
        return BoolSeries(
            value=(
                Comparator(lhs=self.value, operator="__ne__", rhs=None, negated=True)
            )
        )


def _validate_datestring(datestring):
    try:
        datetime.strptime(datestring, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError(
            f"{datestring} is not a valid date; date must in YYYY-MM-DD format"
        )
    return datestring


class DateSeries(PatientSeries):
    @staticmethod
    def _get_other_date_value(other):
        return (
            other.value
            if isinstance(other, DateSeries)
            else _validate_datestring(other)
        )

    def __gt__(self, other: DateSeries | str) -> BoolSeries:
        return BoolSeries(value=self.value > self._get_other_date_value(other))

    def __ge__(self, other: DateSeries | str) -> BoolSeries:
        return BoolSeries(value=self.value >= self._get_other_date_value(other))

    def __lt__(self, other: DateSeries | str) -> BoolSeries:
        return BoolSeries(value=self.value < self._get_other_date_value(other))

    def __le__(self, other: DateSeries | str) -> BoolSeries:
        return BoolSeries(value=self.value <= self._get_other_date_value(other))

    def __ne__(self, other: DateSeries | str) -> BoolSeries:  # type: ignore[override]
        return BoolSeries(value=self.value != self._get_other_date_value(other))

    def round_to_first_of_month(self) -> DateSeries:
        return DateSeries(RoundToFirstOfMonth(self.value))

    def round_to_first_of_year(self) -> DateSeries:
        return DateSeries(RoundToFirstOfYear(self.value))

    @staticmethod
    def _get_other_datedelta_value(delta_value, operation):
        """Ensure we have either a simple int, or an IntSeries representing a date difference in days"""
        if isinstance(delta_value, DateDeltaSeries) and isinstance(
            delta_value.value, DateDifference
        ):
            return delta_value.convert_to_days()
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
                DateDifference(self._get_other_date_value(other), self.value)
            )
        other_value = self._get_other_datedelta_value(other, "subtract")
        return DateSeries(DateSubtraction(self.value, other_value))

    def __rsub__(self, other: str | DateSeries) -> DateDeltaSeries:
        # consistent with python datetime/timedelta, we cannot subtract a DateSeries from
        # anything other than a date or another DateSeries
        try:
            return DateDeltaSeries(
                DateDifference(self.value, self._get_other_date_value(other))
            )
        except ValueError:
            if isinstance(other, str):
                raise
            raise TypeError(
                f"Can't subtract DateSeries from {other.__class__.__name__}"
            )

    def __add__(self, other: DateDeltaSeries | int) -> DateSeries:
        other_value = self._get_other_datedelta_value(other, "add")
        return DateSeries(DateAddition(self.value, other_value))

    def __radd__(self, other: int) -> DateSeries:
        # Note that other cannot be a DateDeltaSeries, as this is handled by DateDeltaSeries.__add__
        return self + other


class DateDeltaSeries(PatientSeries):
    def _convert(self, units):
        if not isinstance(self.value, DateDifference):
            raise ValueError("Can only convert differences between dates")
        start_date, end_date = self.value.arguments[:2]
        return IntSeries(DateDifference(start_date, end_date, units=units))

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
        if isinstance(datedelta, DateDeltaSeries) and isinstance(
            datedelta.value, DateDifference
        ):
            return datedelta.convert_to_days()
        return datedelta

    def __add__(
        self, other: DateDeltaSeries | DateSeries | int
    ) -> DateDeltaSeries | DateSeries:
        # Adding a DateSeries to a DateDeltaSeries should use DateSeries.__add__ to
        # return a new DateSeries
        if isinstance(other, DateSeries):
            return other + self
        return DateDeltaSeries(
            DateDeltaAddition(self._delta_in_days(self), self._delta_in_days(other))
        )

    def __radd__(self, other: int) -> DateDeltaSeries | DateSeries:
        # Note that other cannot be a DateSeries, as this is handled by DateSeries.__add__
        return self + other

    def __sub__(self, other: DateDeltaSeries | int) -> DateDeltaSeries:
        return DateDeltaSeries(
            DateDeltaSubtraction(self._delta_in_days(self), self._delta_in_days(other))
        )

    def __rsub__(
        self, other: str | DateDeltaSeries | int
    ) -> DateSeries | DateDeltaSeries:
        # Note that other cannot be a DateSeries, as this is handled by DateSeries.__sub__
        if isinstance(other, str):
            datestring = _validate_datestring(other)
            # This allows subtraction of a DateDeltaSeries from a date string
            # e.g. 2020-10-01
            return DateSeries(DateSubtraction(datestring, self.convert_to_days()))
        return DateDeltaSeries(
            DateDeltaSubtraction(self._delta_in_days(other), self._delta_in_days(self))
        )


class IdSeries(PatientSeries):
    pass


class IntSeries(PatientSeries):
    def __gt__(self, other: IntSeries | int) -> BoolSeries:
        other_value = other.value if isinstance(other, IntSeries) else other
        return BoolSeries(value=self.value > other_value)

    def __ge__(self, other: IntSeries | int) -> BoolSeries:
        other_value = other.value if isinstance(other, IntSeries) else other
        return BoolSeries(value=self.value >= other_value)

    def __lt__(self, other: IntSeries | int) -> BoolSeries:
        other_value = other.value if isinstance(other, IntSeries) else other
        return BoolSeries(value=self.value < other_value)

    def __le__(self, other: IntSeries | int) -> BoolSeries:
        other_value = other.value if isinstance(other, IntSeries) else other
        return BoolSeries(value=self.value <= other_value)

    def __ne__(self, other: IntSeries | int) -> BoolSeries:  # type: ignore[override]
        other_value = other.value if isinstance(other, IntSeries) else other
        return BoolSeries(value=self.value != other_value)


class FloatSeries(PatientSeries):
    pass


class StrSeries(PatientSeries):
    pass


S = TypeVar("S", bound=PatientSeries)


class Predicate:
    def __init__(
        self,
        column: Column[S],
        operator: str,
        other: str | bool | int | Codelist | None,
    ) -> None:
        self._column = column
        self._operator = operator
        self._other = other

    def apply_to(self, table: BaseTable) -> BaseTable:
        return table.filter(self._column.name, **{self._operator: self._other})


@dataclass
class Column(Generic[S]):
    name: str
    series_type: type[S]

    def is_not_null(self):
        return Predicate(self, "not_equals", None)


class IdColumn(Column[IdSeries]):
    def __init__(self, name):
        return super().__init__(name, IdSeries)


class BoolColumn(Column[BoolSeries]):
    def __init__(self, name):
        return super().__init__(name, BoolSeries)

    def is_true(self) -> Predicate:
        return Predicate(self, "equals", True)

    def is_false(self) -> Predicate:
        return Predicate(self, "equals", False)

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
        return super().__init__(name, DateSeries)

    def __eq__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, "equals", other)

    def __ne__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, "not_equals", other)

    def __gt__(self, other: str) -> Predicate:
        return Predicate(self, "greater_than", other)

    def __ge__(self, other: str) -> Predicate:
        return Predicate(self, "greater_than_or_equals", other)

    def __lt__(self, other: str) -> Predicate:
        return Predicate(self, "less_than", other)

    def __le__(self, other: str) -> Predicate:
        return Predicate(self, "less_than_or_equals", other)


class CodeColumn(Column[CodeSeries]):
    def __init__(self, name):
        return super().__init__(name, CodeSeries)

    def __eq__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, "equals", other)

    def __ne__(self, other: str) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, "not_equals", other)

    def is_in(self, codelist: Codelist) -> Predicate:
        return Predicate(self, "is_in", codelist)


class IntColumn(Column[IntSeries]):
    def __init__(self, name):
        return super().__init__(name, IntSeries)

    def __eq__(self, other: int) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, "equals", other)

    def __ne__(self, other: int) -> Predicate:  # type: ignore[override]  # deliberately inconsistent with object
        return Predicate(self, "not_equals", other)

    def __gt__(self, other: int) -> Predicate:
        return Predicate(self, "greater_than", other)

    def __ge__(self, other: int) -> Predicate:
        return Predicate(self, "greater_than_or_equals", other)

    def __lt__(self, other: int) -> Predicate:
        return Predicate(self, "less_than", other)

    def __le__(self, other: int) -> Predicate:
        return Predicate(self, "less_than_or_equals", other)


class FloatColumn(Column[FloatSeries]):
    def __init__(self, name):
        return super().__init__(name, FloatSeries)


class StrColumn(Column[StrSeries]):
    def __init__(self, name):
        return super().__init__(name, StrSeries)


def not_null_patient_series(patient_series: PatientSeries) -> PatientSeries:
    """
    Generates a new PatientSeries where all null values are removed.

    Args:
        patient_series: PatientSeries that may contain null values

    Returns:
        PatientSeries: A new PatientsSeries without null values
    """
    comparator_value = Comparator(lhs=patient_series.value, operator="__ne__", rhs=None)
    return PatientSeries(value=comparator_value)


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
        if patient_series._is_comparator()
        else not_null_patient_series(patient_series).value
        for key, patient_series in mapping.items()
    }
    return PatientSeries(value=ValueFromCategory(value_mapping, default))


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
