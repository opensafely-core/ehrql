from ..tables import p


title = "Arithmetic operations without division"

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


def test_absolute(spec_test):
    spec_test(
        table_data,
        (p.i1 - 200).absolute(),
        {1: 99, 2: 1},
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


def test_multiply(spec_test):
    spec_test(
        table_data,
        p.i1 * p.i2,
        {1: 101 * 111, 2: None},
    )


def test_multiply_with_constant(spec_test):
    spec_test(
        table_data,
        10 * p.i2,
        {1: 10 * 111, 2: None},
    )
