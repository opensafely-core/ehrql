from ..tables import p

table_data = {
    p: """
          |  i1
        --+-----
        1 | 101
        2 | 201
    """,
}


def test_value_and_patient_series(spec_test):
    spec_test(
        table_data,
        (1 + p.i1).sum_for_patient(),
        {
            1: (1 + 101),
            2: (1 + 201),
        },
    )
