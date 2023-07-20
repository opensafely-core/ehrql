from ehrql import when

from ..tables import p


title = "Case expressions with single condition"


def test_when_with_expression(spec_test):
    table_data = {
        p: """
          | i1
        --+----
        1 | 6
        2 | 7
        3 | 8
        4 |
        """,
    }
    spec_test(
        table_data,
        when(p.i1 < 8).then(p.i1).otherwise(100),
        {
            1: 6,
            2: 7,
            3: 100,
            4: 100,
        },
    )


def test_when_with_boolean_column(spec_test):
    table_data = {
        p: """
              | i1 | b1
            --+----+----
            1 | 6  | T
            2 | 7  | F
            3 |    |
            """,
    }

    spec_test(
        table_data,
        when(p.b1).then(p.i1).otherwise(100),
        {
            1: 6,
            2: 100,
            3: 100,
        },
    )
