import datetime


def year_from_date(date):
    return date.year


def month_from_date(date):
    return date.month


def day_from_date(date):
    return date.day


def date_difference_in_days(end, start):
    return (end - start).days


def date_difference_in_months(end, start):
    year_diff = end.year - start.year
    month_diff = end.month - start.month + 12 * year_diff
    if end.day < start.day:
        return month_diff - 1
    else:
        return month_diff


def date_difference_in_years(end, start):
    year_diff = end.year - start.year
    if (end.month, end.day) < (start.month, start.day):
        return year_diff - 1
    else:
        return year_diff


def date_add_days(date, num_days):
    assert_valid_num_days(num_days)
    return date + datetime.timedelta(days=num_days)


def date_add_weeks(date, num_weeks):
    return date_add_days(date, num_weeks * 7)


def assert_valid_num_days(num_days):
    if abs(num_days) > 999999999:
        raise ValueError(f"Number of days {num_days} is out of range")


def assert_valid_year(year):
    if not 0 < year <= 9999:
        raise ValueError(f"year {year} is out of range")


def date_add_months(date, num_months):
    # Dear me, calendars really are terrible aren't they?
    zero_indexed_month = date.month - 1
    new_zero_indexed_month = zero_indexed_month + num_months
    new_month = 1 + new_zero_indexed_month % 12
    new_year = date.year + new_zero_indexed_month // 12
    assert_valid_year(new_year)
    try:
        return datetime.date(new_year, new_month, date.day)
    except ValueError:
        # We should only ever get an error for a new month which has no corresponding day;
        # in this case we roll forward to the first of the next month.
        # For a defence of this logic see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_months

        # As no month has more days than December we'll never need to roll forward from
        # December and so we don't need to worry about wrapping round to the next year
        assert new_month != 12
        return datetime.date(new_year, new_month + 1, 1)


def date_add_years(date, num_years):
    new_year = date.year + num_years
    assert_valid_year(new_year)
    try:
        return datetime.date(new_year, date.month, date.day)
    except ValueError:
        # We should only ever get an error for 29 Feb on non-leap years, which we want to roll
        # forward to 1 Mar.
        # For a defence of this logic see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_years
        assert date.month == 2 and date.day == 29
        return datetime.date(date.year + num_years, 3, 1)


def to_first_of_year(date):
    return date.replace(day=1, month=1)


def to_first_of_month(date):
    return date.replace(day=1)


def generate_intervals(date_add_fn, base_date, count):
    if count >= 0:
        return [
            (
                date_add_fn(base_date, offset),
                date_add_fn(base_date, offset + 1) - datetime.timedelta(days=1),
            )
            for offset in range(count)
        ]
    else:
        return [
            (
                date_add_fn(base_date, offset - 1) + datetime.timedelta(days=1),
                date_add_fn(base_date, offset),
            )
            for offset in range(1 + count, 1)
        ]
