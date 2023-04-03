from ..tables import e, p


title = "Determining whether a row exists for each patient"

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


def test_exists_for_patient_on_event_frame(spec_test):
    spec_test(
        table_data,
        e.exists_for_patient(),
        {
            1: True,
            2: True,
            3: False,
        },
    )


def test_exists_for_patient_on_patient_frame(spec_test):
    spec_test(
        table_data,
        p.exists_for_patient(),
        {
            1: True,
            2: True,
            3: True,
        },
    )
