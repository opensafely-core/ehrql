from ..tables import p


title = "Combining a patient series with a value"

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
        p.i1 + 1,
        {
            1: (101 + 1),
            2: (201 + 1),
        },
    )


def test_value_and_patient_series(spec_test):
    spec_test(
        table_data,
        1 + p.i1,
        {
            1: (1 + 101),
            2: (1 + 201),
        },
    )
