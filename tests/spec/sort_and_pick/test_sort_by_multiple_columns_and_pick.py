import pytest

from databuilder.query_language import IntSeries
from databuilder.query_model import PickOneRowPerPatient, Position, SelectColumn, Sort

from ..tables import e

title = "Sort by more than one column and pick the first or last row for each patient"

table_data = {
    e: """
          |  i1 | i2
        --+-----+---
        1 | 101 | 3
        1 | 102 | 2
        1 | 102 | 1
        2 | 203 | 1
        2 | 202 | 2
        2 | 202 | 3
        """,
}


@pytest.mark.xfail_in_memory
def test_sort_by_multiple_columns_pick_first(spec_test):
    spec_test(
        table_data,
        e.sort_by(e.i1, e.i2).first_for_patient().i2,
        {
            1: 3,
            2: 2,
        },
    )


@pytest.mark.xfail_in_memory
def test_sort_by_multiple_columns_pick_last(spec_test):
    spec_test(
        table_data,
        e.sort_by(e.i1, e.i2).last_for_patient().i2,
        {
            1: 2,
            2: 1,
        },
    )


# TODO: This isn't actually a spec test and should be moved elsewhere once we have the
# mechanics in place to run non-spec tests against multiple query engines. But I want to
# capture somewhere the currently working behaviour of the in-memory engine and this
# will do for now. Because the kind of sort queries which the in-memory engine can
# handle are inexpressible in ehrQL we have to construct the query directly using the
# Query Model.
def test_sort_using_query_built_directly_in_query_model(spec_test):
    qm_table = e.qm_node
    sort1 = Sort(qm_table, SelectColumn(qm_table, "i2"))
    sort2 = Sort(sort1, SelectColumn(sort1, "i1"))
    pick = PickOneRowPerPatient(sort2, Position.FIRST)
    value = SelectColumn(pick, "i2")
    ehrql_value = IntSeries(value)

    spec_test(
        table_data,
        ehrql_value,
        {
            1: 3,
            2: 2,
        },
    )
