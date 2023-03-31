from ..tables import e, p


title = "Counting the rows for each patient"

table_data = {
    p: """
          | b1
        --+----
        1 |
        2 |
        3 |
        """,
    e: """
          | b1
        --+----
        1 |
        1 |
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
