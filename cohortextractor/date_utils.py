import calendar
import datetime


def generate_date_range(date_range_str):
    # Bail out with an "empty" range: this means we don't need separate
    # codepaths to handle the range, single date, and no date supplied cases
    if not date_range_str:
        return [None]
    start, end, period = _parse_date_range(date_range_str)
    if end < start:
        raise ValueError(
            f"Invalid date range '{date_range_str}': end cannot be earlier than start"
        )
    dates = []
    while start <= end:
        dates.append(start.isoformat())
        start = _increment_date(start, period)
    # The latest data is generally more interesting/useful so we may as well
    # extract that first
    dates.reverse()
    return dates


def _parse_date_range(date_range_str):
    period = "month"
    if " to " in date_range_str:
        start, end = date_range_str.split(" to ", 1)
        if " by " in end:
            end, period = end.split(" by ", 1)
    else:
        start = end = date_range_str
    try:
        start = _parse_date(start)
        end = _parse_date(end)
    except ValueError:
        raise ValueError(
            f"Invalid date range '{date_range_str}': Dates must be in YYYY-MM-DD "
            f"format or 'today' and ranges must be in the form "
            f"'DATE to DATE by (week|month)'"
        )
    if period not in ("week", "month"):
        raise ValueError(f"Unknown time period '{period}': must be 'week' or 'month'")
    return start, end, period


def _parse_date(date_str):
    if date_str == "today":
        return datetime.date.today()
    else:
        return datetime.date.fromisoformat(date_str)


def _increment_date(date, period):
    if period == "week":
        return date + datetime.timedelta(days=7)
    elif period == "month":
        if date.month < 12:
            try:
                return date.replace(month=date.month + 1)
            except ValueError:
                # If the month we've replaced the date in is out of range, it will be at the end
                # of a month which has fewer days than the previous month (e.g. 31st Aug + 1 month)
                # set to last day of previous month instead
                _, last_day_of_month = calendar.monthrange(date.year, date.month)
                return date.replace(day=last_day_of_month)
        else:
            return date.replace(month=1, year=date.year + 1)
    else:
        raise ValueError(f"Unknown time period '{period}'")
