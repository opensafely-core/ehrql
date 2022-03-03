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
        3 | 301 |
        3 | 302 |  F
    """,
}


def test_take_with_column(spec_test):
    spec_test(
        table_data,
        e.take(e.b1).i1.sum_for_patient(),
        {
            1: (101 + 102),
            2: 201,
            3: None,
        },
    )
