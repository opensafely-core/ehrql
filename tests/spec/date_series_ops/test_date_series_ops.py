from datetime import date

from databuilder.ehrql import days

from ..tables import p

title = "Operations which apply to all series containing dates"

table_data = {
    p: """
          |     d1     | i1
        --+------------+-----
        1 | 1990-01-02 | 100
        2 | 2000-03-04 | 200
        3 |            |
        """,
}


def test_get_year(spec_test):
    spec_test(
        table_data,
        p.d1.year,
        {
            1: 1990,
            2: 2000,
            3: None,
        },
    )


def test_get_month(spec_test):
    spec_test(
        table_data,
        p.d1.month,
        {
            1: 1,
            2: 3,
            3: None,
        },
    )


def test_get_day(spec_test):
    spec_test(
        table_data,
        p.d1.day,
        {
            1: 2,
            2: 4,
            3: None,
        },
    )


def test_to_first_of_year(spec_test):
    table_data = {
        p: """
              |     d1
            --+------------
            1 | 1990-01-01
            2 | 2000-12-15
            3 | 2020-12-31
            4 |
            """,
    }
    spec_test(
        table_data,
        p.d1.to_first_of_year(),
        {
            1: date(1990, 1, 1),
            2: date(2000, 1, 1),
            3: date(2020, 1, 1),
            4: None,
        },
    )


def test_to_first_of_month(spec_test):
    table_data = {
        p: """
              |     d1
            --+------------
            1 | 1990-01-01
            2 | 1990-01-31
            3 |
            """,
    }
    spec_test(
        table_data,
        p.d1.to_first_of_month(),
        {
            1: date(1990, 1, 1),
            2: date(1990, 1, 1),
            3: None,
        },
    )


def test_add_days(spec_test):
    spec_test(
        table_data,
        p.d1 + days(p.i1),
        {
            1: date(1990, 4, 12),
            2: date(2000, 9, 20),
            3: None,
        },
    )


def test_subtract_days(spec_test):
    spec_test(
        table_data,
        p.d1 - days(p.i1),
        {
            1: date(1989, 9, 24),
            2: date(1999, 8, 17),
            3: None,
        },
    )


def test_add_date_to_duration(spec_test):
    spec_test(
        table_data,
        days(100) + p.d1,
        {
            1: date(1990, 4, 12),
            2: date(2000, 6, 12),
            3: None,
        },
    )


def test_difference_between_dates_in_years(spec_test):
    # We define "(A - B).years" as the number of entire elapsed calendar years between B
    # and A, as you'd use to calculate someone's age. Note the behaviour specified with
    # respect to leap years: those born on 29 February on a leap year have their
    # birthday on 1 March on non-leap years. Note also the behaviour with respect to
    # negative numbers: if A is earlier than B then the year difference is always
    # negative, even if this difference is only one day.
    table_data = {
        p: """
              |     d1
            --+------------
            1 | 2020-02-29
            2 | 2020-02-28
            3 | 2019-01-01
            4 | 2021-03-01
            5 | 2023-01-01
            6 |
            """,
    }
    spec_test(
        table_data,
        (date(2021, 2, 28) - p.d1).years,
        {
            1: 0,
            2: 1,
            3: 2,
            4: -1,
            5: -2,
            6: None,
        },
    )


def test_difference_between_dates_in_days(spec_test):
    table_data = {
        p: """
              |     d1     |     d2
            --+------------+------------
            1 | 2000-01-01 | 2000-01-01
            2 | 2000-03-01 | 2000-01-01
            3 | 2001-03-01 | 2001-01-01
            4 | 1999-12-31 | 2001-01-01
            """,
    }
    spec_test(
        table_data,
        (p.d1 - p.d2).days,
        {
            1: 0,
            2: 31 + 29,
            3: 31 + 28,
            4: -366 - 1,
        },
    )


def test_reversed_date_differences(spec_test):
    table_data = {
        p: """
              |     d1
            --+------------
            1 | 1990-01-30
            2 | 1970-01-15
            """,
    }
    spec_test(
        table_data,
        (p.d1 - "1980-01-20").years,
        {
            1: 10,
            2: -11,
        },
    )


# DEPRECATED METHODS
#


def test_add_days_method(spec_test):
    spec_test(
        table_data,
        p.d1.add_days(p.i1),
        {
            1: date(1990, 4, 12),
            2: date(2000, 9, 20),
            3: None,
        },
    )


def test_subtract_days_method(spec_test):
    spec_test(
        table_data,
        p.d1.subtract_days(p.i1),
        {
            1: date(1989, 9, 24),
            2: date(1999, 8, 17),
            3: None,
        },
    )


def test_difference_in_years(spec_test):
    # TODO: We should have some text in the documentation explaining that this is
    # "number of entire elapsed years", as you'd use to calculate someone's age, rather
    # than "time difference rounded to nearest year" or anything like that.
    table_data = {
        p: """
              |     d1
            --+------------
            1 | 1990-01-30
            2 | 2000-01-15
            3 | 2020-01-20
            4 | 2022-01-10
            5 |
            """,
    }
    spec_test(
        table_data,
        p.d1.difference_in_years(date(2020, 1, 15)),
        {
            1: 29,
            2: 20,
            3: -1,
            4: -2,
            5: None,
        },
    )
