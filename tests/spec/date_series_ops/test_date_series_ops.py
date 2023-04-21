from datetime import date

from ehrql import days, months, years

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


def test_add_months(spec_test):
    # Below we specify that where adding/subtracting months takes us to a date which
    # doesn't exist (e.g. 31 September, or 29 February on a non-leap year) we roll
    # forward to the first of the next month. As with our definition of year addition
    # below:
    #
    #  1. It is the only behaviour consistent with our "difference in months" definition,
    #     if we define `x + N months` as:
    #
    #       The smallest y such that `(y - x).months == N`
    #
    #  2. It is what SQLite does *in most cases*.  SQLite rolls over to the first of the next
    #     month, except in the case of the last days of February, where the rolled-over date
    #     from 30/31 Feb becomes 02/03 March.
    #
    # Other databases take different approachs so we have to work around their behaviour
    # in their respective query engines, and in the SQLite engine for the end of February
    # behaviour.
    table_data = {
        p: """
          |     d1     | i1
        ---+------------+-----
        1 | 2003-01-29 |  1
        2 | 2004-01-29 |  1
        3 | 2003-01-31 |  1
        4 | 2004-01-31 |  1
        5 | 2004-03-31 | -1
        6 | 2000-10-31 |  11
        7 | 2000-10-31 | -11
        """,
    }
    spec_test(
        table_data,
        p.d1 + months(p.i1),
        {
            1: date(2003, 3, 1),
            2: date(2004, 2, 29),
            3: date(2003, 3, 1),
            4: date(2004, 3, 1),
            5: date(2004, 3, 1),
            6: date(2001, 10, 1),
            7: date(1999, 12, 1),
        },
    )


def test_add_years(spec_test):
    # Below we specify that where adding/subtracting years to 29 February lands us on a
    # non-leap year, we round up to 1 March, rather than down to 28 February. There are
    # various ways of defending this approach:
    #
    #  1. It is the only behaviour consistent with our "difference in years" definition,
    #     if we define `x + N years` as:
    #
    #       The smallest y such that `(y - x).years == N`
    #
    #  2. It is what SQLite does.
    #
    # Other databases take different approachs so we have to work around their behaviour
    # in their respective query engines.
    table_data = {
        p: """
          |     d1     | i1
        --+------------+-----
        1 | 2000-06-15 |  5
        2 | 2000-06-15 | -5
        3 | 2004-02-29 |  1
        4 | 2004-02-29 | -1
        5 | 2004-02-29 |  4
        6 | 2004-02-29 | -4
        7 | 2003-03-01 | 1
        """,
    }
    spec_test(
        table_data,
        p.d1 + years(p.i1),
        {
            1: date(2005, 6, 15),
            2: date(1995, 6, 15),
            3: date(2005, 3, 1),
            4: date(2003, 3, 1),
            5: date(2008, 2, 29),
            6: date(2000, 2, 29),
            7: date(2004, 3, 1),
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


def test_difference_between_dates_in_months(spec_test):
    table_data = {
        p: """
               |     d1     |     d2
            ---+------------+------------
             1 | 2000-02-28 | 2000-01-30
             2 | 2000-03-01 | 2000-01-30
             3 | 2000-03-28 | 2000-02-28
             4 | 2000-03-30 | 2000-01-30
             5 | 2000-02-27 | 2000-01-30
             6 | 2000-01-27 | 2000-01-30
             7 | 1999-12-26 | 2000-01-27
             8 | 2005-02-28 | 2004-02-29
             9 | 2010-01-01 | 2000-01-01
            10 | 2000-01-01 |
            """,
    }
    spec_test(
        table_data,
        (p.d1 - p.d2).months,
        {
            1: 0,
            2: 1,
            3: 1,
            4: 2,
            5: 0,
            6: -1,
            7: -2,
            8: 11,
            9: 120,
            10: None,
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


def test_add_days_to_static_date(spec_test):
    table_data = {
        p: """
          | i1
        --+-----
        1 |  10
        2 | -10
        """,
    }
    spec_test(
        table_data,
        date(2000, 1, 1) + days(p.i1),
        {
            1: date(2000, 1, 11),
            2: date(1999, 12, 22),
        },
    )


def test_add_months_to_static_date(spec_test):
    table_data = {
        p: """
          | i1
        --+-----
        1 |  10
        2 | -10
        """,
    }
    spec_test(
        table_data,
        date(2000, 1, 1) + months(p.i1),
        {
            1: date(2000, 11, 1),
            2: date(1999, 3, 1),
        },
    )


def test_add_years_to_static_date(spec_test):
    table_data = {
        p: """
          | i1
        --+-----
        1 |  10
        2 | -10
        """,
    }
    spec_test(
        table_data,
        date(2000, 1, 1) + years(p.i1),
        {
            1: date(2010, 1, 1),
            2: date(1990, 1, 1),
        },
    )
