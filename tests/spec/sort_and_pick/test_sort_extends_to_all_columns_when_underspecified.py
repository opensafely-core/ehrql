from ..tables import e


title = "Sort extends to all columns when underspecified to ensure that sort order is consistent"

table_data = {
    e: """
          |  i1 | i2 |  i3
        --+----------------
        1 | 100 |  2 | 101
        1 | 100 |  1 | 102
        1 | 100 |  1 | 103
        2 | 100 |  0 | 500
        2 | 100 |  1 |   1
        2 | 101 |  0 |   1
        """,
}


def test_sorting_extends_to_selected_column(spec_test):
    spec_test(
        table_data,
        e.sort_by(e.i1, e.i2).first_for_patient().i3,
        {1: 102, 2: 500},
    )
