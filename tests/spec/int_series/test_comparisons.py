from ..tables import p

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


def test_lt(spec_test):
    spec_test(
        table_data,
        p.i1 < p.i2,
        {1: True, 2: False, 3: False, 4: None},
    )


def test_le(spec_test):
    spec_test(
        table_data,
        p.i1 <= p.i2,
        {1: True, 2: True, 3: False, 4: None},
    )


def test_gt(spec_test):
    spec_test(
        table_data,
        p.i1 > p.i2,
        {1: False, 2: False, 3: True, 4: None},
    )


def test_ge(spec_test):
    spec_test(
        table_data,
        p.i1 >= p.i2,
        {1: False, 2: True, 3: True, 4: None},
    )
