import datetime


def year_from_date(date):
    return date.year


def month_from_date(date):
    return date.month


def day_from_date(date):
    return date.day


def date_difference_in_days(end, start):
    return (end - start).days


def date_difference_in_years(end, start):
    year_diff = end.year - start.year
    if (end.month, end.day) < (start.month, start.day):
        return year_diff - 1
    else:
        return year_diff


def date_add_days(date, num_days):
    return date + datetime.timedelta(days=num_days)


def date_add_years(date, num_years):
    try:
        return datetime.date(date.year + num_years, date.month, date.day)
    except ValueError:
        # We should only ever get an error for 29 Feb on non-leap years, which we want
        # to roll forward to 1 Mar. For a defence of this logic see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_years
        assert date.month == 2 and date.day == 29
        return datetime.date(date.year + num_years, 3, 1)


def to_first_of_year(date):
    return date.replace(day=1, month=1)


def to_first_of_month(date):
    return date.replace(day=1)
