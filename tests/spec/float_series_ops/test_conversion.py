from ..tables import p

title = "Convert a float value"

table_data = {
    p: """
              | i1 | f1
            --+----+----
            1 | 1  | 1.0
            2 | 42 | 32.3
            3 | 3  | 5.8
            4 | -4 | -6.7
            5 |    | -6.2
            6 |    |
            """,
}


def test_float_as_int(spec_test):
    """
    Floats are rounded towards zero.
    """
    spec_test(
        table_data,
        p.f1.as_int(),
        {1: 1, 2: 32, 3: 5, 4: -6, 5: -6, 6: None},
    )


def test_float_as_float(spec_test):
    spec_test(
        table_data,
        p.f1.as_float(),
        {1: 1.0, 2: 32.3, 3: 5.8, 4: -6.7, 5: -6.2, 6: None},
    )


def test_add_float_to_int(spec_test):
    spec_test(
        table_data,
        p.f1 + p.i1.as_float(),
        {1: 2.0, 2: 74.3, 3: 8.8, 4: -10.7, 5: None, 6: None},
    )
