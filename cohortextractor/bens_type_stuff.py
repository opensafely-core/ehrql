from __future__ import annotations

from datetime import date
from typing import Any, Generic, TypeVar


class BaseTable:
    ...


Table = TypeVar("Table", bound=BaseTable)
ColumnType = TypeVar("ColumnType")


class Column(Generic[Table, ColumnType]):
    def __init__(self, name: str) -> None:
        self.name = name


class PatientSeries(Generic[Table, ColumnType]):
    ...


class PatientFrame(Generic[Table]):
    def select_column(
        self, column: Column[Table, ColumnType]
    ) -> PatientSeries[Table, ColumnType]:
        ...


class Cohort:
    def add_variable(
        self, name: str, variable: PatientSeries[Table, ColumnType]
    ) -> None:
        ...

    # Note the looser type here. See below for a partial explanation.
    def __setattr__(self, name: str, variable: PatientSeries[Any, Any]) -> None:
        # I don't know why the call to the more restrictive method type-checks
        self.add_variable(name, variable)


class SortedEventFrame(Generic[Table]):
    def first(self) -> PatientFrame[Table]:
        ...


class EventFrame(Generic[Table]):
    def sort_by(self, column: Column[Table, ColumnType]) -> SortedEventFrame[Table]:
        ...


class EventTable(Generic[Table], BaseTable, EventFrame[Table]):
    ...


class Table1(EventTable["Table1"]):
    date: Column[Table1, date] = Column("date")


class Table2(EventTable["Table2"]):
    date: Column[Table2, date] = Column("date")


table1 = Table1()
table2 = Table2()

cohort = Cohort()

# This only passes mypy because we've loosened the type on __setattr__ to PatientSeries[Any, Any]
cohort.date1 = table1.sort_by(table1.date).first().select_column(table1.date)

# This explicit call to __setattr__ works even with the more restricted type PatientSeries[Table, ColumnType]
cohort.__setattr__(
    "date2", table1.sort_by(table1.date).first().select_column(table1.date)
)

# And this works with an explicit method call and the restricted type
cohort.add_variable(
    "date3", table1.sort_by(table1.date).first().select_column(table1.date)
)

# This line fails mypy (PyCharm also objects):
#     Argument 1 to "select_column" of "PatientFrame" has incompatible type
#     "Column[Immunisations, date]"; expected "Column[OtherEvents, date]"
cohort.date4 = table2.sort_by(table2.date).first().select_column(table1.date)
