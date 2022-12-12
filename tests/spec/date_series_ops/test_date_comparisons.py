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
        p.d1.is_before("2000-01-01"),
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
        p.d1.is_on_or_before("2000-01-01"),
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
        p.d1.is_after("2000-01-01"),
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
        p.d1.is_on_or_after("2000-01-01"),
        {
            1: False,
            2: True,
            3: True,
            4: None,
        },
    )


def test_is_before_with_str_date(spec_test):
    spec_test(
        table_data,
        p.d1 < "2000-01-01",
        {
            1: True,
            2: False,
            3: False,
            4: None,
        },
    )


def test_is_on_or_before_with_str_date(spec_test):
    spec_test(
        table_data,
        p.d1 <= "2000-01-01",
        {
            1: True,
            2: True,
            3: False,
            4: None,
        },
    )


def test_is_after_with_str_date(spec_test):
    spec_test(
        table_data,
        p.d1 > "2000-01-01",
        {
            1: False,
            2: False,
            3: True,
            4: None,
        },
    )


def test_is_on_or_after_with_str_date(spec_test):
    spec_test(
        table_data,
        p.d1 >= "2000-01-01",
        {
            1: False,
            2: True,
            3: True,
            4: None,
        },
    )


def test_is_equal_with_str_date(spec_test):
    spec_test(
        table_data,
        p.d1 == "2000-01-01",
        {
            1: False,
            2: True,
            3: False,
            4: None,
        },
    )


def test_is_in_dates(spec_test):
    dates = [date(2010, 1, 1), date(2010, 1, 2)]
    spec_test(
        table_data,
        p.d1.is_in(dates),
        {
            1: False,
            2: False,
            3: True,
            4: None,
        },
    )

    dates = [date(2010, 1, 2), date(2010, 1, 3)]
    spec_test(
        table_data,
        p.d1.is_in(dates),
        {
            1: False,
            2: False,
            3: False,
            4: None,
        },
    )


def test_is_in_strings(spec_test):
    d = ["2010-01-01", "2010-01-02"]
    spec_test(
        table_data,
        p.d1.is_in(d),
        {1: False, 2: False, 3: True, 4: None},
    )

    d = ["2010-01-02", "2010-01-03"]
    spec_test(
        table_data,
        p.d1.is_in(d),
        {1: False, 2: False, 3: False, 4: None},
    )
