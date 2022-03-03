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


def test_value_and_event_series(spec_test):
    spec_test(
        table_data,
        (1 + e.i1).sum_for_patient(),
        {
            1: (1 + 101) + (1 + 102),
            2: (1 + 201) + (1 + 202),
        },
    )
