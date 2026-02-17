from ..tables import p


title = "Arithmetic operations without division"

table_data = {
    p: """
          |  f1   |  f2
        --+-------+-------
        1 | 101.3 | 111.5
        2 | 201.4 |
        """,
}


def test_negate(spec_test):
    spec_test(
        table_data,
        -p.f2,
        {1: -111.5, 2: None},
    )


def test_absolute(spec_test):
    spec_test(
        table_data,
        (p.f1 - 200.0).absolute(),
        {1: 98.7, 2: 1.4},
    )


def test_add(spec_test):
    spec_test(
        table_data,
        p.f1 + p.f2,
        {1: 101.3 + 111.5, 2: None},
    )


def test_subtract_with_positive_result(spec_test):
    spec_test(
        table_data,
        p.f2 - p.f1,
        {1: 111.5 - 101.3, 2: None},
    )


def test_subtract_with_negative_result(spec_test):
    spec_test(
        table_data,
        p.f1 - p.f2,
        {1: 101.3 - 111.5, 2: None},
    )


def test_multiply(spec_test):
    spec_test(
        table_data,
        p.f1 * p.f2,
        {1: 101.3 * 111.5, 2: None},
    )


def test_multiply_with_constant(spec_test):
    spec_test(
        table_data,
        10.0 * p.f2,
        {1: 10.0 * 111.5, 2: None},
    )
