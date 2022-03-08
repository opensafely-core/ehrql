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


def test_drop_with_expr(spec_test):
    spec_test(
        table_data,
        e.drop((e.i1 + e.i2) < 413).i1.sum_for_patient(),
        {
            1: None,
            2: (202 + 203),
            3: 301,
        },
    )
