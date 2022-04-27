from ..tables import e, p

title = "Determining whether a row exists for each patient"

# Although we ensure that there is a row of p for each row of e in run_test(), we
# explictly create rows of p here, since we want to check that the correct data is
# returned for a patient that has no data in e.

# We also need to explicitly specify a population that includes all patients because
# the variable doesn't mention the patients table.

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


def test_exists_for_patient(spec_test):
    spec_test(
        table_data,
        e.exists_for_patient(),
        {
            1: True,
            2: True,
            3: False,
        },
        population=~p.patient_id.is_null(),
    )
