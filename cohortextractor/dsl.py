"""This module provides classes for building a cohort using the DSL.

Data lives in database tables, which are represented by PatientTable (a table with one
row per patient) and EventTable (a table with multiple rows per patient).

Through filtering, sorting, aggregating, and selecting columns, we transform instances
of PatientTable/EventTable into instances of PatientSeries.

A PatientSeries represents a mapping between patients and values, and can be assigned to
a Cohort.  In the future, a PatientSeries will be able to be combined with another
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

from cohortextractor.query_language import BaseTable as QMBaseTable
from cohortextractor.query_language import Row
from cohortextractor.query_language import Table as QMTable
from cohortextractor.query_language import Value, ValueFromAggregate


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
        self.__dict__[name] = variable


class PatientFrame:
    """Represents a collection of records, with one row per patient.

    Either a PatientTable, or the result of filtering a PatientTable.
    """

    # TODO


class EventFrame:
    """Represents a collection of records, with multiple rows per patient.

    Either an EventTable, or the result of filtering an EventTable.
    """

    def __init__(self, qm_table: QMBaseTable):
        self.qm_table = qm_table

    def filter(self, column: str, **kwargs: str) -> EventFrame:  # noqa: A003
        """Return a new EventFrame with given filter."""

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

    def __init__(self, qm_table: QMBaseTable, *sort_columns: str):
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


class BaseTable:
    """A base class for database tables."""

    def __init__(self, name: str):
        self.name = name
        self.qm_table: QMBaseTable = QMTable(name)


class EventTable(BaseTable, EventFrame):
    """A base class for database tables with multiple rows per patient."""


class PatientTable(BaseTable, PatientFrame):
    """A base class for database tables with one row per patient."""
