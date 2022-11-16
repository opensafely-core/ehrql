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


def to_first_of_year(date):
    return date.replace(day=1, month=1)


def to_first_of_month(date):
    return date.replace(day=1)
