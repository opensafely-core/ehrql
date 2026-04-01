from ..tables import p


title = "Raise a value to a power"


table_data = {
    p: """
          |  f1   |  f2
        --+-------+--------
        1 |   2   |  111
        2 | 120   |   -2
        3 |-101   |   10
        4 | -10   |   -1
        5 | -10   |
        6 |       |  -10
        7 |   0   |  -20
        8 | -20   |    0
        """,
}


def test_power(spec_test):
    spec_test(
        table_data,
        p.f1**p.f2,
        {
            1: 2**111,
            2: 120**-2,
            3: (-101) ** 10,
            4: (-10) ** (-1),
            5: None,
            6: None,
            7: None,
            8: (-20) ** 0,
        },
    )


def test_raise_series_to_a_constant(spec_test):
    spec_test(
        table_data,
        p.f1**10,
        {
            1: 2**10,
            2: 120**10,
            3: (-101) ** 10,
            4: (-10) ** 10,
            5: (-10) ** 10,
            6: None,
            7: 0**10,
            8: (-20) ** 10,
        },
    )


def test_raise_constant_to_a_series(spec_test):
    spec_test(
        table_data,
        10**p.f1,
        {
            1: 10**2,
            2: 10**120,
            3: 10 ** (-101),
            4: 10 ** (-10),
            5: 10 ** (-10),
            6: None,
            7: 10**0,
            8: 10 ** (-20),
        },
    )
