from ..tables import e


title = "Combining two event series"

table_data = {
    e: """
          |  i1 |  i2 | s1
        --+-----+-----+---
        1 | 101 | 111 | b
        1 | 102 | 112 | a
        2 | 201 | 211 | b
        2 | 202 | 212 | a
    """,
}


def test_event_series_and_event_series(spec_test):
    spec_test(
        table_data,
        (e.i1 + e.i2).sum_for_patient(),
        {
            1: (101 + 111) + (102 + 112),
            2: (201 + 211) + (202 + 212),
        },
    )


def test_event_series_and_sorted_event_series(spec_test):
    """
    The sort order of the underlying event series does not affect their combination.
    """
    spec_test(
        table_data,
        (e.i1 + e.sort_by(e.s1).i2).minimum_for_patient(),
        {
            1: (101 + 111),
            2: (201 + 211),
        },
    )
