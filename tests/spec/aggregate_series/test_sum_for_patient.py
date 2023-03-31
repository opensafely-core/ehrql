from ..tables import e


title = "Sum aggregation"

table_data = {
    e: """
          |  i1
        --+-----
        1 | 101
        1 | 102
        1 | 103
        2 | 201
        2 |
        2 | 203
        3 |
        """,
}


def test_sum_for_patient(spec_test):
    spec_test(
        table_data,
        e.i1.sum_for_patient(),
        {
            1: (101 + 102 + 103),
            2: (201 + 203),
            3: None,
        },
    )
