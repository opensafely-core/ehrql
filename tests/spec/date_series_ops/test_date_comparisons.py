from datetime import date

from ..tables import p

title = "Comparisons involving dates"

table_data = {
    p: """
          |     d1
        --+------------
        1 | 1990-01-01
        2 | 2000-01-01
        3 | 2010-01-01
        4 |
        """,
}


def test_is_before(spec_test):
    spec_test(
        table_data,
        p.d1.is_before(date(2000, 1, 1)),
        {
            1: True,
            2: False,
            3: False,
            4: None,
        },
    )


def test_is_on_or_before(spec_test):
    spec_test(
        table_data,
        p.d1.is_on_or_before(date(2000, 1, 1)),
        {
            1: True,
            2: True,
            3: False,
            4: None,
        },
    )


def test_is_after(spec_test):
    spec_test(
        table_data,
        p.d1.is_after(date(2000, 1, 1)),
        {
            1: False,
            2: False,
            3: True,
            4: None,
        },
    )


def test_is_on_or_after(spec_test):
    spec_test(
        table_data,
        p.d1.is_on_or_after(date(2000, 1, 1)),
        {
            1: False,
            2: True,
            3: True,
            4: None,
        },
    )
