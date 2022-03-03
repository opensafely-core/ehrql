from ..tables import e

table_data = {
    e: """
          |  i1
        --+-----
        1 | 101
        1 | 102
        2 | 201
        2 | 202
    """,
}


def test_event_series_and_value(spec_test):
    spec_test(
        table_data,
        (e.i1 + 1).sum_for_patient(),
        {
            1: (101 + 1) + (102 + 1),
            2: (201 + 1) + (202 + 1),
        },
    )
