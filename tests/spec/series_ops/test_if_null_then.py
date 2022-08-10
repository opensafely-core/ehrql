from ..tables import p

title = "Replace missing values"

table_data = {
    p: """
          |  i1
        --+-----
        1 | 101
        2 | 201
        3 | 301
        4 |
        """,
}


def test_if_null_then_integer_column(spec_test):
    spec_test(
        table_data,
        p.i1.if_null_then(0),
        {
            1: 101,
            2: 201,
            3: 301,
            4: 0,
        },
    )


def test_if_null_then_boolean_column(spec_test):
    spec_test(
        table_data,
        p.i1.is_in([101, 201]).if_null_then(False),
        {
            1: True,
            2: True,
            3: False,
            4: False,
        },
    )
