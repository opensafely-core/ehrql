from ..tables import p


title = "Raise a value to a power"


table_data = {
    p: """
          |  f1   |  f2
        --+-------+--------
        1 |   2.5 |  111.5
        2 | 120.4 |   -2.5
        3 |-101.3 |   10.3
        4 | -10.3 |   -1.5
        5 | -10.3 |
        6 |       |  -10.3
        7 |   0.0 |  -20.3
        8 | -20.3 |    0.0
        """,
}


def test_power(spec_test):
    spec_test(
        table_data,
        p.f1**p.f2,
        {
            1: 2.5**111.5,
            2: 120.4 ** (-2.5),
            3: None,
            4: None,
            5: None,
            6: None,
            7: None,
            8: (-20.3) ** 0.0,
        },
    )


def test_raise_series_to_a_constant(spec_test):
    spec_test(
        table_data,
        p.f1**10.0,
        {
            1: 2.5**10.0,
            2: 120.4**10.0,
            3: (-101.3) ** 10.0,
            4: (-10.3) ** 10.0,
            5: (-10.3) ** 10.0,
            6: None,
            7: 0.0**10.0,
            8: (-20.3) ** 10.0,
        },
    )


def test_raise_constant_to_a_series(spec_test):
    spec_test(
        table_data,
        10.0**p.f1,
        {
            1: 10.0**2.5,
            2: 10.0**120.4,
            3: 10.0 ** (-101.3),
            4: 10.0 ** (-10.3),
            5: 10.0 ** (-10.3),
            6: None,
            7: 10.0**0.0,
            8: 10.0 ** (-20.3),
        },
    )
