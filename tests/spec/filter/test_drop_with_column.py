from ..tables import e

table_data = {
    e: """
          |  i1 |  b1
        --+-----+-----
        1 | 101 |  T
        1 | 102 |  T
        1 | 103 |
        2 | 201 |  T
        2 | 202 |
        2 | 203 |  F
        3 | 301 |  T
        3 | 302 |  T
    """,
}


def test_drop_with_column(spec_test):
    spec_test(
        table_data,
        e.drop(e.b1).i1.sum_for_patient(),
        {
            1: 103,
            2: (202 + 203),
            3: None,
        },
    )
