from ..tables import e, p

title = "Count the rows for each patient"

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


def test_count_for_patient_on_event_frame(spec_test):
    spec_test(
        table_data,
        e.count_for_patient(),
        {
            1: 2,
            2: 1,
            3: 0,
        },
    )


def test_count_for_patient_on_patient_frame(spec_test):
    spec_test(
        table_data,
        p.count_for_patient(),
        {
            1: 1,
            2: 1,
            3: 1,
        },
    )
