from ..tables import p

title = "Convert a float value"


def test_float_as_int(spec_test):
    """
    Floats are rounded towards zero.
    """
    table_data = {
        p: """
              | f1
            --+--------
            1 | 1.0
            2 | 32.3
            3 | 5.8
            4 | -6.7
            5 | -6.2
            6 |
            """,
    }
    spec_test(
        table_data,
        p.f1.as_int(),
        {1: 1, 2: 32, 3: 5, 4: -6, 5: -6, 6: None},
    )


def test_float_as_float(spec_test):
    table_data = {
        p: """
              | f1
            --+--------
            1 | 1.0
            2 | 32.3
            3 | 5.8
            4 | -6.7
            5 | -6.2
            6 |
            """,
    }
    spec_test(
        table_data,
        p.f1.as_float(),
        {1: 1.0, 2: 32.3, 3: 5.8, 4: -6.7, 5: -6.2, 6: None},
    )
