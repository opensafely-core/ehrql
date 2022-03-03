from ..tables import e

table_data = {
    e: """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        1 | 102 | 112
        2 | 201 | 211
        2 | 202 | 212
    """,
}


def test_event_series_and_event_series(spec_test):
    spec_test(
        table_data,
        (e.i1 + e.i2).sum_for_patient(),
        {
            1: (101 + 111) + (102 + 112),
            2: (201 + 211) + (202 + 212),
        },
    )
