from ..tables import p

table_data = {
    p: """
          |  i1
        --+-----
        1 | 101
        2 | 201
    """,
}


def test_patient_series_and_value(spec_test):
    spec_test(
        table_data,
        (p.i1 + 1).sum_for_patient(),
        {
            1: (101 + 1),
            2: (201 + 1),
        },
    )
