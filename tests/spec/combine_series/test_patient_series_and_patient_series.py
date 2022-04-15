import pytest

from ..tables import p

title = "Combining two patient series"

table_data = {
    p: """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 102
        2 | 201 | 202
    """,
}


@pytest.mark.sql_spec
def test_patient_series_and_patient_series(spec_test):
    spec_test(
        table_data,
        (p.i1 + p.i2).sum_for_patient(),
        {
            1: (101 + 102),
            2: (201 + 202),
        },
    )
