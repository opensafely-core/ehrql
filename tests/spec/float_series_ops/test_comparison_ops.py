from ..tables import p

title = "Comparison operations"

table_data = {
    p: """
          |  f1 |  f2
        --+-----+-----
        1 | 101.1 | 201.2
        2 | 201.2 | 201.2
        3 | 301.3 | 201.2
        4 |       | 201.2
        """,
}


def test_less_than(spec_test):
    spec_test(
        table_data,
        p.f1 < p.f2,
        {1: True, 2: False, 3: False, 4: None},
    )


def test_less_than_or_equal_to(spec_test):
    spec_test(
        table_data,
        p.f1 <= p.f2,
        {1: True, 2: True, 3: False, 4: None},
    )


def test_greater_than(spec_test):
    spec_test(
        table_data,
        p.f1 > p.f2,
        {1: False, 2: False, 3: True, 4: None},
    )


def test_greater_than_or_equal_to(spec_test):
    spec_test(
        table_data,
        p.f1 >= p.f2,
        {1: False, 2: True, 3: True, 4: None},
    )
