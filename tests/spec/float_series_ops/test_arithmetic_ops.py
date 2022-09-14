from ..tables import p

title = "Arithmetic operations"

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
