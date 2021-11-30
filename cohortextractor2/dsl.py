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
    boolean_comparator,
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

    def filter(  # noqa: A003
        self,
        column_or_expr: str | CodelistFilterExpr,
        **kwargs: str | Codelist,
    ) -> EventFrame:
        """Return a new EventFrame with given filter.

        Note that while we are building the DSL, this method takes either an expression
        (at the moment, just a CodelistFilterExpr is supported) or it takes arguments
        that are passed directly to the corresponding QM filter method.

        Once we fully support filtering with expressions, we can rename column_or_expr
        to expr, and drop kwargs.
        """

        if isinstance(column_or_expr, CodelistFilterExpr):
            assert not kwargs
            column = column_or_expr.column
            kwargs = {"is_in": column_or_expr.codelist}
        else:
            column = column_or_expr
        return EventFrame(self.qm_table.filter(column, **kwargs))

    def sort_by(self, *columns: str) -> SortedEventFrame:
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

    def __init__(self, qm_table: BaseTable, *sort_columns: str):
        self.qm_table = qm_table
        self.sort_columns = sort_columns

    def first_for_patient(self) -> AggregatedEventFrame:
        """Return a AggregatedEventFrame with the first event for each patient."""

        return AggregatedEventFrame(row=self.qm_table.first_by(*self.sort_columns))

    def last_for_patient(self) -> AggregatedEventFrame:
        """Return a AggregatedEventFrame with the last event for each patient."""

        return AggregatedEventFrame(row=self.qm_table.last_by(*self.sort_columns))


class AggregatedEventFrame:
    def __init__(self, row: Row):
        self.row = row

    def filter(self, column: str, **kwargs: str) -> AggregatedEventFrame:  # noqa: A003
        """Return a new AggregatedEventFrame with given filter."""
        # TODO

    def select_column(self, column: str) -> PatientSeries:
        """Return a PatientSeries containing given column."""

        return PatientSeries(self.row.get(column))


class PatientSeries:
    """Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """

    def __init__(self, value: Value):
        self.value = value

    @staticmethod
    def _get_other(other: Expression) -> bool | str | int | Value:
        if isinstance(other, PatientSeries):
            return other.value
        return other

    def __gt__(self, other: Expression) -> Comparator:
        return self.value > self._get_other(other)

    def __ge__(self, other: Expression) -> Comparator:
        return self.value >= self._get_other(other)

    def __lt__(self, other: Expression) -> Comparator:
        return self.value < self._get_other(other)

    def __le__(self, other: Expression) -> Comparator:
        return self.value <= self._get_other(other)

    def __eq__(self, other: Expression) -> Comparator:  # type: ignore[override]
        return self.value == self._get_other(other)

    def __ne__(self, other: Expression) -> Comparator:  # type: ignore[override]
        return self.value != self._get_other(other)

    def __and__(self, other: Expression) -> Comparator:
        return self.value & self._get_other(other)

    def __or__(self, other: Expression) -> Comparator:
        return self.value | self._get_other(other)

    def __invert__(self) -> Comparator:
        return ~self.value


def categorise(mapping: dict[str, Expression], default: bool | None) -> PatientSeries:
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
    mapping = {
        key: boolean_comparator(mapped_value.value)
        if isinstance(mapped_value, PatientSeries)
        else mapped_value
        for key, mapped_value in mapping.items()
    }
    return PatientSeries(value=ValueFromCategory(mapping, default))


class codelist:
    """A wrapper around Codelist, with a .contains method for use with .filter()."""

    def __init__(self, codes: list[str], system: str):
        self.codelist = codelistlib.codelist(codes, system)

    def contains(self, column: str) -> CodelistFilterExpr:
        return CodelistFilterExpr(self.codelist, column)


@dataclass
class CodelistFilterExpr:
    codelist: Codelist
    column: str


Expression = Union[PatientSeries, CodelistFilterExpr, bool, int, str]
