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

from typing import NoReturn, Union


class Cohort:
    """Represents the cohort of patients in a study."""

    def set_population(self, population: PatientSeries) -> None:
        """Set the population variable for this cohort."""

    def add_variable(self, name: str, variable: PatientSeries) -> None:
        """Add a variable to this cohort by name."""

    def __setattr__(self, name: str, variable: PatientSeries) -> None:
        return self.add_variable(name, variable)


class EventFrame:
    """Represents a collection of records, with multiple rows per patient.

    Either an EventTable, or the result of filtering an EventTable.
    """

    def filter(self, filter: Expression) -> EventFrame:  # noqa: A002, A003
        """Return a new EventFrame with given filter."""

    def sort_by(self, *columns: ColumnOrName) -> SortedEventFrame:
        """Return a SortedEventFrame with given sort column."""

    def count(self) -> PatientSeries:
        """Return a PatientSeries with count of matching events per patient."""

    def exists(self) -> PatientSeries:
        """Return a PatientSeries indicating whether each patient has a matching event."""

    def __getattr__(self, name: str) -> NoReturn:
        ...


class SortedEventFrame:
    """Represents an EventFrame that has been sorted."""

    def first(self) -> PatientFrame:
        """Return a PatientFrame with the first event for each patient."""

    def last(self) -> PatientFrame:
        """Return a PatientFrame with the last event for each patient."""

    def __getattr__(self, name: str) -> NoReturn:
        ...


class PatientFrame:
    """Represents a collection of records, with one row per patient.

    Either a PatientTable, or the result of filtering a PatientTable.
    """

    def filter(self, filter: Expression) -> PatientFrame:  # noqa: A002, A003
        """Return a new PatientFrame with given filter.

        >>> filtered = table.filter(table.code in codes)
        """

    def select_column(self, column: ColumnOrName) -> PatientSeries:
        """Return a PatientSeries containing given column.

        >>> column = table.select_column(table.date)
        >>> column = table.select_column("date")
        """

    def __getattr__(self, name: str) -> NoReturn:
        ...


class PatientSeries:
    """Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """

    def __eq__(self, other: Expression) -> PatientSeries:  # type: ignore
        """Return Expression indicating whether self is equal to other."""

    def __ne__(self, other: Expression) -> PatientSeries:  # type: ignore
        ...

    def __add__(self, other: Expression) -> PatientSeries:
        ...

    def __gt__(self, other: Expression) -> PatientSeries:
        ...

    # etc

    def __getattr__(self, name: str) -> NoReturn:
        ...


class BaseTable:
    """A base class for database tables."""


class EventTable(BaseTable, EventFrame):
    """A base class for database tables with multiple rows per patient."""


class PatientTable(BaseTable, PatientFrame):
    """A base class for database tables with one row per patient."""


class Column(PatientSeries):
    """Represents a column in a database table."""

    def __init__(self, name: str) -> None:
        self.name = name


ColumnOrName = Union[Column, str]
Expression = Union[PatientSeries, bool, int, str]


class Codelist:
    def __init__(self, codes: list[str]) -> None:
        self.codes = codes

    def __contains__(self, code: ColumnOrName) -> Expression:
        """Return Expression indicating whether code in this codelist."""


def categorise(mapping: dict[str, Expression]) -> PatientSeries:
    """Represents a switch statement."""
