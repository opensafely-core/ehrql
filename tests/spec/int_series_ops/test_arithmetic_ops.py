from ..tables import p

title = "Arithmetic operations"

table_data = {
    p: """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        2 | 201 |
        """,
}


def test_negate(spec_test):
    spec_test(
        table_data,
        -p.i2,
        {1: -111, 2: None},
    )


def test_add(spec_test):
    spec_test(
        table_data,
        p.i1 + p.i2,
        {1: 101 + 111, 2: None},
    )


def test_subtract(spec_test):
    spec_test(
        table_data,
        p.i1 - p.i2,
        {1: 101 - 111, 2: None},
    )
