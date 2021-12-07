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
from typing import Union

from . import codelistlib
from .query_language import (
    BaseTable,
    Codelist,
    Comparator,
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


class EventFrame:
    """Represents an unsorted collection of records, with multiple rows per patient."""

    def __init__(self, qm_table: BaseTable):
        self.qm_table = qm_table

    def filter(  # noqa: A003
        self,
        column_or_expr: Column | CodelistFilterExpr,
        **kwargs: str | Codelist | None | bool,
    ) -> EventFrame:
        """Return a new EventFrame with given filter.

        Note that while we are building the DSL, this method takes either an expression
        (at the moment, just a CodelistFilterExpr is supported) or it takes arguments
        that are passed directly to the corresponding QM filter method.

        Once we fully support filtering with expressions, we can rename column_or_expr
        to expr, and drop kwargs.
        """

        column: Column
        if isinstance(column_or_expr, CodelistFilterExpr):
            assert not kwargs
            column = column_or_expr.column
            kwargs = {"is_in": column_or_expr.codelist}
        else:
            column = column_or_expr
        return EventFrame(self.qm_table.filter(column.name, **kwargs))

    def sort_by(self, *columns: Column) -> SortedEventFrame:
        """Return a SortedEventFrame with given sort column."""

        return SortedEventFrame(self.qm_table, *columns)

    def count_for_patient(self) -> PatientSeries:
        """Return a PatientSeries with count_for_patient of matching events per patient."""

        return PatientSeries(self.qm_table.count())

    def exists_for_patient(self) -> PatientSeries:
        """Return a PatientSeries indicating whether each patient has a matching event."""

        return PatientSeries(self.qm_table.exists())


class SortedEventFrame:
    """Represents an EventFrame that has been sorted."""

    def __init__(self, qm_table: BaseTable, *sort_columns: Column):
        self.qm_table = qm_table
        self.sort_columns = sort_columns

    def first_for_patient(self) -> PatientFrame:
        """Return a PatientFrame with the first event for each patient."""

        return PatientFrame(row=self.qm_table.first_by(*self._sort_column_names()))

    def last_for_patient(self) -> PatientFrame:
        """Return a PatientFrame with the last event for each patient."""

        return PatientFrame(row=self.qm_table.last_by(*self._sort_column_names()))

    def _sort_column_names(self):
        return [c.name for c in self.sort_columns]


class PatientFrame:
    """Represents an unsorted collection of records, with one row per patient."""

    def __init__(self, row: Row):
        self.row = row

    def select_column(self, column: Column) -> PatientSeries:
        """Return a PatientSeries containing given column."""

        return PatientSeries(self.row.get(column.name))


class PatientSeries:
    """Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """

    def __init__(self, value: Value | Comparator):
        self.value = value

    def _is_comparator(self) -> bool:
        return isinstance(self.value, Comparator)

    def __gt__(self, other: ValueExpression) -> PatientSeries:
        return PatientSeries(value=self.value > other)

    def __ge__(self, other: ValueExpression) -> PatientSeries:
        return PatientSeries(value=self.value >= other)

    def __lt__(self, other: ValueExpression) -> PatientSeries:
        return PatientSeries(value=self.value < other)

    def __le__(self, other: ValueExpression) -> PatientSeries:
        return PatientSeries(value=self.value <= other)

    def __eq__(self, other: ValueExpression) -> PatientSeries:  # type: ignore[override]
        # All python objects have __eq__ and __ne__ defined, so overriding these method s
        # involves overriding them on a superclass (`object`), which results in
        # a typing error as it violates the violates the Liskov substitution principle
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        # We are deliberately overloading the operators here, hence the ignore
        return PatientSeries(value=self.value == other)

    def __ne__(self, other: ValueExpression) -> PatientSeries:  # type: ignore[override]
        return PatientSeries(value=self.value != other)

    def __and__(self, other: PatientSeries) -> PatientSeries:
        return PatientSeries(value=self.value & other.value)

    def __or__(self, other: PatientSeries) -> PatientSeries:
        return PatientSeries(value=self.value | other.value)

    def __invert__(self) -> PatientSeries:
        if self._is_comparator():
            comparator_value = ~self.value
        else:
            comparator_value = Comparator(
                lhs=self.value, operator="__ne__", rhs=None, negated=True
            )
        return PatientSeries(value=comparator_value)

    def __repr__(self) -> str:
        return f"PatientSeries(value={self.value})"

    def __hash__(self) -> int:
        return hash(repr(self.value))


@dataclass
class Column:
    name: str


class IdColumn(Column):
    ...


class BoolColumn(Column):
    ...


class DateColumn(Column):
    ...


class CodeColumn(Column):
    ...


class IntColumn(Column):
    ...


def not_null_patient_series(patient_series: PatientSeries) -> PatientSeries:
    comparator_value = Comparator(lhs=patient_series.value, operator="__ne__", rhs=None)
    return PatientSeries(value=comparator_value)


def categorise(
    mapping: dict[Expression, PatientSeries], default: Expression | None = None
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
    mapping: dict[Expression, PatientSeries], default: Expression | None
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

    def contains(self, column: CodeColumn) -> CodelistFilterExpr:
        return CodelistFilterExpr(self.codelist, column)


@dataclass
class CodelistFilterExpr:
    codelist: Codelist
    column: CodeColumn


ValueExpression = Union[PatientSeries, Comparator, str, int]
Expression = Union[str, int, float, bool]
