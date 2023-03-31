from ..tables import p


title = "Comparison operations"

table_data = {
    p: """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 201
        2 | 201 | 201
        3 | 301 | 201
        4 |     | 201
        """,
}


def test_less_than(spec_test):
    spec_test(
        table_data,
        p.i1 < p.i2,
        {1: True, 2: False, 3: False, 4: None},
    )


def test_less_than_or_equal_to(spec_test):
    spec_test(
        table_data,
        p.i1 <= p.i2,
        {1: True, 2: True, 3: False, 4: None},
    )


def test_greater_than(spec_test):
    spec_test(
        table_data,
        p.i1 > p.i2,
        {1: False, 2: False, 3: True, 4: None},
    )


def test_greater_than_or_equal_to(spec_test):
    spec_test(
        table_data,
        p.i1 >= p.i2,
        {1: False, 2: True, 3: True, 4: None},
    )
