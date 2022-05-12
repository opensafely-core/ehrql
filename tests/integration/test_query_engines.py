import sqlalchemy

from databuilder.query_model import (
    AggregateByPatient,
    Filter,
    Function,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Sort,
    Value,
)

from ..lib.mock_backend import EventLevelTable


# The in-memory query engine does not currently work with multiple sort operations where
# the sort column is selected from the base table each time. However it does work
# correctly when each sort column is selected from the result of the immediately
# preceeding sort operation. As this latter style of query is impossible to construct
# using ehrQL we include a test that builds the query directly using the Query Model to
# capture what is currently working correctly in the in-memory engine.
#
# This is the working version of xfailed test at:
#
#   tests/spec/sort_and_pick/test_sort_by_multiple_columns_and_pick.py::test_sort_by_multiple_columns_pick_first[in_memory]
#
def test_sort_without_using_chained_operations(engine):
    engine.setup(
        EventLevelTable(PatientId=1, i1=101, i2=3),
        EventLevelTable(PatientId=1, i1=102, i2=2),
        EventLevelTable(PatientId=1, i1=102, i2=1),
        EventLevelTable(PatientId=2, i1=203, i2=1),
        EventLevelTable(PatientId=2, i1=202, i2=2),
        EventLevelTable(PatientId=2, i1=202, i2=3),
    )

    table = SelectTable("event_level_table")
    sort1 = Sort(table, SelectColumn(table, "i2"))
    sort2 = Sort(sort1, SelectColumn(sort1, "i1"))
    pick = PickOneRowPerPatient(sort2, Position.FIRST)

    variables = dict(
        population=AggregateByPatient.Exists(table),
        v=SelectColumn(pick, "i2"),
    )

    results = {r["patient_id"]: r["v"] for r in engine.extract_qm(variables)}
    assert results == {
        1: 3,
        2: 2,
    }


# As above, this is the working version of the xfailed test at:
#
#  tests/spec/filter/test_take.py::test_chain_multiple_takes[in_memory]
#
def test_multiple_takes_without_chaining(engine):
    engine.setup(
        EventLevelTable(PatientId=1, i1=1, b1=True),
        EventLevelTable(PatientId=1, i1=2, b1=True),
        EventLevelTable(PatientId=1, i1=3, b1=False),
    )

    table = SelectTable("event_level_table")
    filter1 = Filter(table, Function.GE(SelectColumn(table, "i1"), Value(2)))
    filter2 = Filter(filter1, SelectColumn(filter1, "b1"))
    values = SelectColumn(filter2, "i1")

    variables = dict(
        population=AggregateByPatient.Exists(table),
        v=AggregateByPatient.Sum(values),
    )

    results = {r["patient_id"]: r["v"] for r in engine.extract_qm(variables)}
    assert results == {
        1: 2,
    }


def test_handles_degenerate_poppulaton(engine):
    engine.setup(metadata=sqlalchemy.MetaData())
    variables = dict(
        population=Value(False),
        v=Value(1),
    )
    assert engine.extract_qm(variables) == []
