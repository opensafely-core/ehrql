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


def test_sort_by_multiple_columns_pick_first(spec_test):
    spec_test(
        table_data,
        e.sort_by(e.i1, e.i2).first_for_patient().i2,
        {
            1: 3,
            2: 2,
        },
    )


def test_sort_by_multiple_columns_pick_last(spec_test):
    spec_test(
        table_data,
        e.sort_by(e.i1, e.i2).last_for_patient().i2,
        {
            1: 2,
            2: 1,
        },
    )
