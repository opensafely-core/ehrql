from ..tables import e


title = "Mean aggregation"

table_data = {
    e: """
          | i1 | f1
        --+----+-----
        1 |  1 | 1.1
        1 |  2 | 2.1
        1 |  3 | 3.1
        2 |    |
        2 |  2 | 2.1
        2 |  3 | 3.1
        3 |    |
        """,
}


def test_mean_for_patient_integer(spec_test):
    spec_test(
        table_data,
        e.i1.mean_for_patient(),
        {
            1: (1 + 2 + 3) / 3,
            2: (2 + 3) / 2,
            3: None,
        },
    )


def test_mean_for_patient_float(spec_test):
    spec_test(
        table_data,
        e.f1.mean_for_patient(),
        {
            1: (1.1 + 2.1 + 3.1) / 3,
            2: (2.1 + 3.1) / 2,
            3: None,
        },
    )
