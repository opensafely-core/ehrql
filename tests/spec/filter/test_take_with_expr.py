from ..tables import e

table_data = {
    e: """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        1 | 102 | 112
        1 | 103 | 113
        2 | 201 | 211
        2 | 202 | 212
        2 | 203 | 213
        3 | 301 |
    """,
}


def test_take_with_expr(spec_test):
    spec_test(
        table_data,
        e.take((e.i1 + e.i2) < 413).i1.sum_for_patient(),
        {
            1: (101 + 102 + 103),
            2: 201,
            3: None,
        },
    )
