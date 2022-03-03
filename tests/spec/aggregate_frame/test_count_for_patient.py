from ..tables import e, p

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


def test_count_for_patient(spec_test):
    spec_test(
        table_data,
        e.count_for_patient(),
        {
            1: 2,
            2: 1,
            3: 0,
        },
    )
