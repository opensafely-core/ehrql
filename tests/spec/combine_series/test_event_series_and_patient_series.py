from ..tables import e, p


title = "Combining an event series with a patient series"

table_data = {
    p: """
          |  i1
        --+-----
        1 | 101
        2 | 201

    """,
    e: """
          |  i1
        --+-----
        1 | 111
        1 | 112
        2 | 211
        2 | 212
    """,
}


def test_event_series_and_patient_series(spec_test):
    spec_test(
        table_data,
        (e.i1 + p.i1).sum_for_patient(),
        {
            1: (111 + 101) + (112 + 101),
            2: (211 + 201) + (212 + 201),
        },
    )


def test_patient_series_and_event_series(spec_test):
    spec_test(
        table_data,
        (p.i1 + e.i1).sum_for_patient(),
        {
            1: (101 + 111) + (101 + 112),
            2: (201 + 211) + (201 + 212),
        },
    )
