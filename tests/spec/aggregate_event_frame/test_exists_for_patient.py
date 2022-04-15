import pytest

from ..tables import e, p

title = "Determining whether a row exists for each patient"

# Although we ensure that there is a row of p for each row of e in run_test(), we
# explictly create rows of p here, since we want to check that the correct data is
# returned for a patient that has no data in e.

# Additionally, creating the rows of p in run_test() is expected to be a temporary
# measure until Dataset.use_unrestricted_population() works for all QEs.

table_data = {
    p: """
          | i1
        --+----
        1 | 101
        2 | 201
        3 | 301
        """,
    e: """
          | b1
        --+----
        1 |  T
        1 |  F
        2 |
        """,
}


@pytest.mark.sql_spec
def test_exists_for_patient(spec_test):
    spec_test(
        table_data,
        e.exists_for_patient(),
        {
            1: True,
            2: True,
            3: False,
        },
    )
