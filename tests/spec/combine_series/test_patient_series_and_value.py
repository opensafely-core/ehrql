import pytest

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


@pytest.mark.sql_spec
def test_patient_series_and_value(spec_test):
    spec_test(
        table_data,
        (p.i1 + 1).sum_for_patient(),
        {
            1: (101 + 1),
            2: (201 + 1),
        },
    )


@pytest.mark.sql_spec
def test_value_and_patient_series(spec_test):
    spec_test(
        table_data,
        (1 + p.i1).sum_for_patient(),
        {
            1: (1 + 101),
            2: (1 + 201),
        },
    )
