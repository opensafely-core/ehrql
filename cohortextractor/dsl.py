"""This module provides classes for building a cohort using the DSL and compiling it.

Data lives in database tables, which are represented by PatientTable (a table with one
row per patient) and EventTable (a table with multiple rows per patient).

Through filtering, sorting, aggregating, and selecting columns, we transform instances
of PatientTable/EventTable into instances of PatientSeries.

A PatientSeries represents a mapping between patients and values, and can be assigned to
a Cohort.  In the future, a PatientSeries will be able to be combined with another
PatientSeries or a scalar value to produce a new PatientSeries.

All classes except Cohort are intended to be immutable.

Methods are designed so that users can only perform actions that are semantically
meaningful.  This means that the order of operations is restricted.  In a terrible ASCII
railway diagram:

     +------------------------------------+
     |                                    |
     |                      filter        |
     |                    +--------+      |
     |                    |        |      |
     |        filter      |        v      |    select_column
PatientTable ----------> PatientFrame ----+-------------------> PatientSeries
                            ^                                       ^
                            |                                       |
                            | first_for_patient,                    |
                            | last_for_patient                      |
                            |                                       |
                    SortedEventFrame                                |
                            ^                                       |
                            |                                       |
                            | sort_by                               |
                            |                                       |
                            |                                       |
            filter          |                                       |
EventTable --------> EventFrame --------+---------------------------+
     |                |      ^          |     count_for_patient,
     |                |      |          |     exists_for_patient
     |                +------+          |
     |                 filter           |
     |                                  |
     +----------------------------------+

All the classes in this diagram have a _path attribute.  As methods are called on
objects of these classes, the _path attribute is updated, so that the _path of a
PatientSeries contains all the information about how to generate the PatientSeries from
the original PatientTable/EventTable.

For instance:

    >>> e = tables.clinical_events
    >>> series = e.sort_by(e.date).first_for_patient().select_column(e.code)
    >>> for item in series._path:
            print(item)
    (<concepts.tables.ClinicalEvents object at 0x7f211195fbb0>, 'sort_by', ('date',), {})
    (<dsl.SortedEventFrame object at 0x7f211198d5b0>, 'first_for_patient', (), {})
    (<dsl.PatientFrame object at 0x7f211198d610>, 'select_column', ('code',), {})

When we compile a PatientSeries into a query_language.Value, we iterate over the path to
build the appropriate Query Model objects.

For each public DSL method on the DSL classes, there is a corresponding "private"
compilation method that gets called in compilation to build an Query Model object.

For instance, PatientFrame.select_column returns a PatientSeries, while
PatientFrame._select_column is passed a query_language.Row, and calls .get on it to
return a query_language.ValueFromRow.

In some cases, we are not able to build the appropriate Query Model objects straight
away.  An example of this is EventFrame._sort_by: in the Query Model, sorting happens in
BaseTable.first_by, but when _sort_by is called, we don't know whether the user has
requested the first or the last row for each patient.  To handle this, each compilation
function can set some state which is passed to subsequent compilation functions, and in
this example, _sort_by adds sort_columns to the state.

Other notes...

To support providing helpful error messages, we can implement __getattr__ on each class.
This will intercept any lookup of a missing attribute, so that if eg a user tries to
select a column from a SortedEventFrame, we can tell them they need to aggregate the
SortedEventFrame first_for_patient.

This docstring, and the function docstrings in this module are not currently intended
for end users.
"""

from __future__ import annotations

from typing import Any

from cohortextractor.query_language import BaseTable as QMTable
from cohortextractor.query_language import (
    QueryNode,
    Row,
    Table,
    Value,
    ValueFromAggregate,
    ValueFromRow,
)


class Cohort:
    """Represents the cohort of patients in a study."""

    def set_population(self, population: PatientSeries) -> None:
        """Set the population variable for this cohort."""

    def add_variable(self, name: str, variable: PatientSeries) -> None:
        """Add a variable to this cohort by name."""
        object.__setattr__(self, name, variable)

    def __setattr__(self, name: str, variable: PatientSeries) -> None:
        return self.add_variable(name, variable)


class Node:
    name: str

    def __init__(
        self,
        parent: Node,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        self._path: list[PathItem] = parent._path + [
            (parent, method_name, args, kwargs)
        ]


PathItem = tuple[Node, str, Any, Any]
State = dict[str, Any]


class EventFrame(Node):
    """Represents a collection of records, with multiple rows per patient.

    Either an EventTable, or the result of filtering an EventTable.
    """

    def filter(self, column: str, **kwargs: str) -> EventFrame:  # noqa: A003
        """Return a new EventFrame with given filter."""

        return EventFrame(self, "filter", column, **kwargs)

    def sort_by(self, *columns: str) -> SortedEventFrame:
        """Return a SortedEventFrame with given sort column."""

        return SortedEventFrame(self, "sort_by", *columns)

    def count_for_patient(self) -> PatientSeries:
        """Return a PatientSeries with count_for_patient of matching events per patient."""

        return PatientSeries(self, "count_for_patient")

    def exists_for_patient(self) -> PatientSeries:
        """Return a PatientSeries indicating whether each patient has a matching event."""

        return PatientSeries(self, "exists_for_patient")

    def _filter(
        self,
        table: QMTable,
        state: State,
        column: str,
        **kwargs: str,
    ) -> tuple[QMTable, State]:
        if kwargs.get("not_equals", object()) is None:
            assert "not_null_filter" not in state
            extra_state = {"not_null_filter": column}
        else:
            extra_state = {}
        return table.filter(column, **kwargs), extra_state

    def _sort_by(
        self,
        table: QMTable,
        state: State,
        *columns: str,
    ) -> tuple[QMTable, State]:
        return table, {"sort_columns": columns}

    def _exists_for_patient(
        self,
        table: QMTable,
        state: State,
    ) -> tuple[ValueFromAggregate, State]:
        return table.exists(state["not_null_filter"]), {}

    def _count_for_patient(
        self,
        table: QMTable,
        state: State,
    ) -> tuple[ValueFromAggregate, State]:
        return table.count(state["not_null_filter"]), {}


class SortedEventFrame(Node):
    """Represents an EventFrame that has been sorted."""

    def first_for_patient(self) -> PatientFrame:
        """Return a PatientFrame with the first_for_patient event for each patient."""

        return PatientFrame(self, "first_for_patient")

    def last_for_patient(self) -> PatientFrame:
        """Return a PatientFrame with the last_for_patient event for each patient."""

        return PatientFrame(self, "last_for_patient")

    def _first_for_patient(
        self,
        table: QMTable,
        state: State,
    ) -> tuple[Row, State]:
        return table.first_by(*state["sort_columns"]), {}

    def _last_for_patient(
        self,
        table: QMTable,
        state: State,
    ) -> tuple[Row, State]:
        return table.last_by(*state["sort_columns"]), {}


class PatientFrame(Node):
    """Represents a collection of records, with one row per patient.

    Either a PatientTable, or the result of filtering a PatientTable.
    """

    def filter(self, column: str, **kwargs: str) -> PatientFrame:  # noqa: A003
        """Return a new PatientFrame with given filter."""

        return PatientFrame(self, "filter", column, **kwargs)

    def select_column(self, column: str) -> PatientSeries:
        """Return a PatientSeries containing given column."""

        return PatientSeries(self, "select_column", column)

    def _filter(
        self,
        table: QMTable,
        state: State,
        column: str,
        **kwargs: str,
    ) -> tuple[QMTable, State]:
        if kwargs.get("not_equals", object()) is None:
            assert "not_null_filter" not in state
            extra_state = {"not_null_filter": column}
        else:
            extra_state = {}
        return table.filter(column, **kwargs), extra_state

    def _select_column(
        self,
        row: Row,
        state: State,
        column: str,
    ) -> tuple[ValueFromRow, State]:
        return row.get(column), {}


class PatientSeries(Node):
    """Represents a column indexed by patient.

    Can be used as a variable in a Cohort, or as an input when computing another
    variable.
    """


class BaseTable:
    """A base class for database tables."""

    def __init__(self, name):
        self.name = name
        self._path = []


class EventTable(BaseTable, EventFrame):
    """A base class for database tables with multiple rows per patient."""


class PatientTable(BaseTable, PatientFrame):
    """A base class for database tables with one row per patient."""


def compile(cohort: Cohort) -> dict[str, Value]:  # noqa: A001
    """Return a dict mapping variable names to Query Model values."""

    return {k: compile_variable(v._path) for k, v in vars(cohort).items()}


def compile_variable(path: list[PathItem]) -> Value:
    """Return the Query Model value for this variable."""

    obj: QueryNode = Table(path[0][0].name)
    state: State = {}

    for node, method_name, args, kwargs in path:
        method = getattr(node, "_" + method_name)
        obj, extra_state = method(obj, state, *args, **kwargs)
        state.update(extra_state)

    assert isinstance(obj, Value)
    return obj
