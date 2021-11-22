"""Skeleton classes and types for the DSL.

This module contains classes and types for building a cohort.

An example of the DSL in use is in cohortextractor/dsl_example.py.

Data lives in database tables, which are represented by PatientTable (a table with one
row per patient) and EventTable (a table with multiple rows per patient).

Through filtering, sorting, aggregating, and selecting columns, we transform instances
of PatientTable/EventTable into instances of PatientSeries.

A PatientSeries represents a mapping between patients and values, and can be assigned to
a Cohort. A PatientSeries can also be combined with another PatientSeries or a scalar
value to produce a new PatientSeries.

All classes except Cohort are intended to be immutable.

Methods are designed so that users can only perform actions that are semantically
meaningful.  This means that the order of operations is restricted.  In a terrible ASCII
railway diagram:

             (  filter                )*  select_column
PatientTable ( --------> PatientFrame )  ---------------> PatientSeries
                            ^                                   ^
                            |                                   |
                            | first, last                       |
                            |                                   |
                            |                                   |
                    SortedEventFrame                            |
                            ^                                   |
                            |                                   |
                            | sort_by                           |
                            |                                   |
                            |                                   |
           (  filter              )*        count, exists       |
EventTable ( --------> EventFrame )  ---------------------------+

To support providing helpful error messages, we can implement __getattr__ on each class.
This will intercept any lookup of a missing attribute, so that if eg a user tries to
select a column from a SortedEventFrame, we can tell them they need to aggregate the
SortedEventFrame first.
"""

from __future__ import annotations

import functools
from datetime import date
from typing import Generic, NoReturn, TypeVar, Union


class BaseTable:
    """A base class for database tables."""


Table = TypeVar("Table", bound=BaseTable)
ColumnType = TypeVar("ColumnType", str, int, bool, date)


class Cohort:
    """Represents the cohort of patients in a study."""

    @functools.lru_cache
    def set_population(self, population: PatientSeries[Table, bool]) -> None:
        """Set the population variable for this cohort."""

    def add_variable(
        self, name: str, variable: PatientSeries[Table, ColumnType]
    ) -> None:
        """Add a variable to this cohort by name."""

    def __setattr__(
        self, name: str, variable: PatientSeries[Table, ColumnType]
    ) -> None:
        return self.add_variable(name, variable)


class EventFrame(Generic[Table]):
    """Represents a collection of records, with multiple rows per patient.

    Either an EventTable, or the result of filtering an EventTable.
    """

    # noinspection PyShadowingBuiltins
    def filter(
        self, filter: Expression[Table, ColumnType, bool]
    ) -> EventFrame[Table]:  # noqa: A002, A003
        """Return a new EventFrame with given filter."""

    def sort_by(self, *columns: Column[Table, ColumnType]) -> SortedEventFrame[Table]:
        """Return a SortedEventFrame with given sort column."""

    def count(self) -> PatientSeries[Table, int]:
        """Return a PatientSeries with count of matching events per patient."""

    def exists(self) -> PatientSeries[Table, bool]:
        """Return a PatientSeries indicating whether each patient has a matching event."""

    def __getattr__(self, name: str) -> NoReturn:
        ...


class SortedEventFrame(Generic[Table]):
    """Represents an EventFrame that has been sorted."""

    def first(self) -> PatientFrame[Table]:
        """Return a PatientFrame with the first event for each patient."""

    def last(self) -> PatientFrame[Table]:
        """Return a PatientFrame with the last event for each patient."""

    def __getattr__(self, name: str) -> NoReturn:
        ...


class PatientFrame(Generic[Table]):
    """Represents a collection of records, with one row per patient.

    Either a PatientTable, or the result of filtering a PatientTable.
    """

    # noinspection PyShadowingBuiltins
    def filter(self, filter: Expression) -> PatientFrame[Table]:  # noqa: A002, A003
        """Return a new PatientFrame with given filter."""

    def select_column(
        self, column: Column[Table, ColumnType]
    ) -> PatientSeries[Table, ColumnType]:
        """Return a PatientSeries containing given column."""

    def __getattr__(self, name: str) -> NoReturn:
        ...


class PatientSeries(Generic[Table, ColumnType]):
    """Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """

    def __eq__(
        self, other: PatientSeries[Table, ColumnType]
    ) -> Expression[Table, ColumnType, bool]:
        """Return Expression indicating whether self is equal to other."""

    def __ne__(
        self, other: PatientSeries[Table, ColumnType]
    ) -> Expression[Table, ColumnType, bool]:
        ...

    def __add__(self, other: Expression | int) -> PatientSeries:
        ...

    def __gt__(self, other: Expression) -> PatientSeries:
        ...

    # etc

    def __getattr__(self, name: str) -> NoReturn:
        ...


class EventTable(BaseTable, EventFrame):
    """A base class for database tables with multiple rows per patient."""


class PatientTable(BaseTable, PatientFrame):
    """A base class for database tables with one row per patient."""


class Column(Generic[Table, ColumnType]):
    """Represents a column in a database table."""

    def __init__(self, name: str) -> None:
        self.name = name


U = TypeVar("U")
V = TypeVar("V")


class Expression(Generic[Table, U, V]):
    ...


class Codelist:
    def __init__(self, codes: list[str]) -> None:
        self.codes = codes

    def __contains__(self, code: Column[Table, str]) -> Expression[Table, str, bool]:
        """Return Expression indicating whether code in this codelist."""


# noinspection PyUnusedLocal
def categorise(
    mapping: dict[str, Expression[Table, U, bool]]
) -> PatientSeries[Table, bool]:
    """Represents a switch statement."""
