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


def test_is_in(spec_test):
    spec_test(
        table_data,
        p.d1.is_in([date(2010, 1, 1), date(1900, 1, 1)]),
        {
            1: False,
            2: False,
            3: True,
            4: None,
        },
    )


def test_is_not_in(spec_test):
    spec_test(
        table_data,
        p.d1.is_not_in([date(2010, 1, 1), date(1900, 1, 1)]),
        {
            1: True,
            2: True,
            3: False,
            4: None,
        },
    )


table_data_for_between_tests = {
    p: """
          |     d1
        --+------------
        1 | 2010-01-01
        2 | 2010-01-02
        3 | 2010-01-03
        4 | 2010-01-04
        5 | 2010-01-05
        6 |
        """,
}


def test_is_between_but_not_on(spec_test):
    table_data = table_data_for_between_tests
    spec_test(
        table_data,
        p.d1.is_between_but_not_on(date(2010, 1, 2), date(2010, 1, 4)),
        {
            1: False,
            2: False,
            3: True,
            4: False,
            5: False,
            6: None,
        },
    )


def test_is_on_or_between(spec_test):
    table_data = table_data_for_between_tests
    spec_test(
        table_data,
        p.d1.is_on_or_between(date(2010, 1, 2), date(2010, 1, 4)),
        {
            1: False,
            2: True,
            3: True,
            4: True,
            5: False,
            6: None,
        },
    )


def test_is_during(spec_test):
    table_data = table_data_for_between_tests
    interval = (
        date(2010, 1, 2),
        date(2010, 1, 4),
    )
    spec_test(
        table_data,
        p.d1.is_during(interval),
        {
            1: False,
            2: True,
            3: True,
            4: True,
            5: False,
            6: None,
        },
    )


def test_is_on_or_between_backwards(spec_test):
    table_data = table_data_for_between_tests
    spec_test(
        table_data,
        p.d1.is_on_or_between(date(2010, 1, 4), date(2010, 1, 2)),
        {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: None,
        },
    )
