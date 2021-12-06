"""This module provides classes for building a cohort using the DSL.

Database tables are modeled by PatientFrame (a collection of records with one record per
patient) and EventFrame (a collection of records with multiple records per patient).

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
      filter |  PatientFrame
             |   |   |
             +---+   | select_column
                     V
                PatientSeries


             +---+
             |   V
      filter |  EventFrame -----------------------+
             |   |   |                            |
             +---+   | sort_by                    |
                     V                            |
             SortedEventFrame                     |
                     |                            |
        +---+        | (first/last)_for_patient   | (count/exists)_for_patient
        |   V        V                            |
 filter |  AggregatedEventFrame                   |
        |   |        |                            |
        +---+        | select_column              |
                     V                            |
               PatientSeries <--------------------+


To support providing helpful error messages, we can implement __getattr__ on each class.
This will intercept any lookup of a missing attribute, so that if eg a user tries to
select a column from a SortedEventFrame, we can tell them they need to aggregate the
SortedEventFrame first_for_patient.

This docstring, and the function docstrings in this module are not currently intended
for end users.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Mapping, TypeVar, Union, cast, overload

from . import codelistlib
from .query_language import (
    BaseTable,
    Codelist,
    Comparator,
    DateDiffValue,
    IntDiffValue,
    IntLtValue,
    PuntedValue,
    Row,
    Value,
    ValueFromAggregate,
    ValueFromCategory,
)


class Cohort:
    """Represents the cohort of patients in a study."""

    def set_population(self, population: PatientSeries) -> None:
        """Set the population variable for this cohort."""

        self.population = population
        value = population.value

        if not (isinstance(value, ValueFromAggregate) and value.function == "exists"):
            raise ValueError(
                "Population variable must return a boolean. Did you mean to use `exists_for_patient()`?"
            )

    def add_variable(self, name: str, variable: PatientSeries) -> None:
        """Add a variable to this cohort by name."""

        self.__setattr__(name, variable)

    def __setattr__(self, name: str, variable: PatientSeries) -> None:
        if not isinstance(variable, PatientSeries):
            raise TypeError(
                f"{name} must be a single value per patient (got '{variable.__class__.__name__}')"
            )
        super().__setattr__(name, variable)


class PatientFrame:
    """Represents an unsorted collection of records, with one row per patient."""

    # TODO


class EventFrame:
    """Represents an unsorted collection of records, with multiple rows per patient."""

    def __init__(self, qm_table: BaseTable):
        self.qm_table = qm_table

    def filter(self, predicate: Predicate) -> EventFrame:  # noqa: A003
        """Return a new EventFrame with given filter."""
        return EventFrame(predicate.apply_to(self.qm_table))

    def sort_by(self, *columns: Column[S]) -> SortedEventFrame:
        """Return a SortedEventFrame with given sort column."""

        return SortedEventFrame(self.qm_table, *columns)

    def count_for_patient(self) -> IntSeries:
        """Return a PatientSeries with count_for_patient of matching events per patient."""

        return IntSeries(self.qm_table.count())

    def exists_for_patient(self) -> BoolSeries:
        """Return a PatientSeries indicating whether each patient has a matching event."""

        return BoolSeries(self.qm_table.exists())


class SortedEventFrame:
    """Represents an EventFrame that has been sorted."""

    def __init__(self, qm_table: BaseTable, *sort_columns: Column[S]):
        self.qm_table = qm_table
        self.sort_columns = sort_columns

    def first_for_patient(self) -> AggregatedEventFrame:
        """Return a AggregatedEventFrame with the first event for each patient."""

        return AggregatedEventFrame(
            row=self.qm_table.first_by(*self._sort_column_names())
        )

    def last_for_patient(self) -> AggregatedEventFrame:
        """Return a AggregatedEventFrame with the last event for each patient."""

        return AggregatedEventFrame(
            row=self.qm_table.last_by(*self._sort_column_names())
        )

    def _sort_column_names(self):
        return [c.name for c in self.sort_columns]


class AggregatedEventFrame:
    def __init__(self, row: Row):
        self.row = row

    def filter(self, column: str, **kwargs: str) -> AggregatedEventFrame:  # noqa: A003
        """Return a new AggregatedEventFrame with given filter."""
        # TODO

    def select_column(self, column: Column[S]) -> S:
        """Return a PatientSeries containing given column."""

        return column.series_type(self.row.get(column.name))


class PatientSeries:
    """Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """

    def __init__(self, value: Value | Comparator):
        self.value = value

    def _is_comparator(self) -> bool:
        return isinstance(self.value, Comparator)

    def __repr__(self) -> str:
        return f"PatientSeries(value={self.value})"

    def __hash__(self) -> int:
        return hash(repr(self.value))


class BoolSeries(PatientSeries):
    def __eq__(self, other: ValueExpression) -> BoolSeries:  # type: ignore[override]
        # All python objects have __eq__ and __ne__ defined, so overriding these method s
        # involves overriding them on a superclass (`object`), which results in
        # a typing error as it violates the violates the Liskov substitution principle
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        # We are deliberately overloading the operators here, hence the ignore
        return BoolSeries(value=self.value == other)

    def __ne__(self, other: ValueExpression) -> BoolSeries:  # type: ignore[override]
        return BoolSeries(value=self.value != other)

    @overload
    def __and__(self, other: BoolSeries) -> BoolSeries:
        ...

    @overload
    def __and__(self, other: bool) -> BoolSeries:
        ...

    def __and__(self, other: BoolSeries | bool) -> BoolSeries:
        if isinstance(other, BoolSeries):
            return BoolSeries(value=self.value & other.value)
        if isinstance(other, bool):
            return BoolSeries(PuntedValue(self.value, other))

    def __or__(self, other: BoolSeries) -> BoolSeries:
        return BoolSeries(value=self.value | other.value)

    def __invert__(self) -> BoolSeries:
        if self._is_comparator():
            comparator_value = ~self.value
        else:
            comparator_value = Comparator(
                lhs=self.value, operator="__ne__", rhs=None, negated=True
            )
        return BoolSeries(value=comparator_value)


class DateSeries(PatientSeries):
    def __gt__(self, other: ValueExpression) -> BoolSeries:
        return BoolSeries(value=self.value > other)

    def __ge__(self, other: ValueExpression) -> BoolSeries:
        return BoolSeries(value=self.value >= other)

    def __lt__(self, other: ValueExpression) -> BoolSeries:
        return BoolSeries(value=self.value < other)

    def __le__(self, other: ValueExpression) -> BoolSeries:
        return BoolSeries(value=self.value <= other)

    def __eq__(self, other: ValueExpression) -> BoolSeries:  # type: ignore[override]
        # All python objects have __eq__ and __ne__ defined, so overriding these method s
        # involves overriding them on a superclass (`object`), which results in
        # a typing error as it violates the violates the Liskov substitution principle
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        # We are deliberately overloading the operators here, hence the ignore
        return BoolSeries(value=self.value == other)

    def __ne__(self, other: ValueExpression) -> BoolSeries:  # type: ignore[override]
        return BoolSeries(value=self.value != other)

    def __sub__(self, other: DateSeries) -> DateDiffSeries:
        return DateDiffSeries(DateDiffValue(self.value, other.value))


class DateDiffSeries(PatientSeries):
    ...


class CodeSeries(PatientSeries):
    def __eq__(self, other: str) -> BoolSeries:  # type: ignore[override]
        return BoolSeries(PuntedValue(self.value, other))

    def __ne__(self, other: str | None) -> BoolSeries:  # type: ignore[override]
        return BoolSeries(PuntedValue(self.value, other))

    def __and__(self, other: BoolSeries) -> BoolSeries:
        return BoolSeries(value=not_null_patient_series(self).value & other.value)

    def __invert__(self) -> BoolSeries:
        return BoolSeries(
            value=(
                Comparator(lhs=self.value, operator="__ne__", rhs=None, negated=True)
            )
        )


class IdSeries(PatientSeries):
    ...


class IntSeries(PatientSeries):
    def __sub__(self, other: int) -> IntSeries:
        return IntSeries(IntDiffValue(self.value, other))

    def __lt__(self, other: int) -> BoolSeries:
        return BoolSeries(IntLtValue(self.value, other))

    def __le__(self, other: int) -> BoolSeries:
        return BoolSeries(PuntedValue(self.value, other))

    def __gt__(self, other: int) -> BoolSeries:
        return BoolSeries(PuntedValue(self.value, other))

    def __ge__(self, other: int) -> BoolSeries:
        return BoolSeries(PuntedValue(self.value, other))

    def __eq__(self, other: int) -> BoolSeries:  # type: ignore[override]
        return BoolSeries(PuntedValue(self.value, other))


S = TypeVar("S", bound=PatientSeries)


@dataclass
class Column(Generic[S]):
    name: str
    series_type: type[S]


class DateColumn(Column[DateSeries]):
    def __init__(self, name):
        super().__init__(name, DateSeries)

    def __gt__(self, other: str) -> Predicate:
        return Predicate(self, "greater_than", other)

    def __lt__(self, other: str) -> Predicate:
        return Predicate(self, "less_than", other)


class CodeColumn(Column[CodeSeries]):
    def __init__(self, name):
        super().__init__(name, CodeSeries)

    def __ne__(self, other: Codelist | None) -> Predicate:  # type: ignore[override]  # already defined on object
        return Predicate(self, "not_equals", other)


class BoolColumn(Column[BoolSeries]):
    def __init__(self, name):
        super().__init__(name, BoolSeries)

    def __eq__(self, other: bool) -> Predicate:  # type: ignore[override]  # already defined on object
        return Predicate(self, "equals", other)


class IdColumn(Column[IdSeries]):
    def __init__(self, name):
        super().__init__(name, IdSeries)


class IntColumn(Column[IntSeries]):
    def __init__(self, name):
        super().__init__(name, IntSeries)


class Predicate:
    def __init__(
        self, column: Column[S], operator: str, other: str | bool | Codelist | None
    ) -> None:
        self._column = column
        self._operator = operator
        self._other = other

    def apply_to(self, table: BaseTable) -> BaseTable:
        return cast(
            BaseTable, table.filter(self._column.name, **{self._operator: self._other})
        )


def not_null_patient_series(patient_series: PatientSeries) -> PatientSeries:
    comparator_value = Comparator(lhs=patient_series.value, operator="__ne__", rhs=None)
    return PatientSeries(value=comparator_value)


Expression = Union[str, int, float, bool]
E = TypeVar("E", bound=Expression)


def categorise(
    mapping: Mapping[E, BoolSeries | CodeSeries], default: E | None = None
) -> PatientSeries:
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


def _validate_category_mapping(
    mapping: Mapping[E, BoolSeries | CodeSeries], default: E | None
) -> None:
    """
    Ensure that a category mapping is valid, by checking that:
    - there are no duplicate values
    - all keys are the same type
    - all values are PatientSeries
    - default value is None, or the same type as the keys
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
    """Recursively raise any category errors found"""
    if not errors:
        return
    try:
        next_category_error = errors.pop()
        raise next_category_error
    finally:
        raise_category_errors(errors)


class codelist:
    """A wrapper around Codelist, with a .contains method for use with .filter()."""

    def __init__(self, codes: list[str], system: str):
        self.codelist = codelistlib.codelist(codes, system)

    def contains(self, column: CodeColumn) -> Predicate:
        return Predicate(column, "is_in", self.codelist)


ValueExpression = Union[PatientSeries, Comparator, str, int]
