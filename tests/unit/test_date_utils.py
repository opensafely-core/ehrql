import pytest

from databuilder import dataset_date_range


@pytest.mark.freeze_time("2021-02-01")
@pytest.mark.parametrize(
    "args,expected",
    [
        (
            ("2021-01-01", "2021-03-10", "month"),
            ["2021-01-01", "2021-02-01", "2021-03-01"],
        ),
        (("2021-01-01", "2021-03-01"), ["2021-01-01", "2021-02-01", "2021-03-01"]),
        (("2021-01-01", "today", "month"), ["2021-01-01", "2021-02-01"]),
        (
            ("2021-01-01", "2021-02-15", "week"),
            [
                "2021-01-01",
                "2021-01-08",
                "2021-01-15",
                "2021-01-22",
                "2021-01-29",
                "2021-02-05",
                "2021-02-12",
            ],
        ),
        (("2021-01-31", "2021-03-01", "month"), ["2021-01-31", "2021-02-28"]),
        (
            ("2021-12-15", "2022-03-01", "month"),
            ["2021-12-15", "2022-01-15", "2022-02-15"],
        ),
        (("2021-01-01",), ["2021-01-01"]),
    ],
    ids=[
        "test date range by month",
        "test date range default increment (month)",
        "test date range end today",
        "test date range by week",
        "test date range corrects out of range dates to last day of month",
        "test date range corrects out of range month to first month of next year",
        "test single date",
    ],
)
def test_extracts_data_with_index_date_range_integration_test(args, expected):
    assert dataset_date_range(*args) == expected


@pytest.mark.parametrize(
    "args,error,error_message",
    [
        (
            ("2021-01-01", "2021-02-31", "month"),
            ValueError,
            "Invalid date '2021-02-31': Dates must be in YYYY-MM-DD",
        ),
        (
            ("2021-01-01", "2021-02-20", "year"),
            ValueError,
            "Unknown time period 'year': must be 'week' or 'month'",
        ),
        (
            ("2021-01-01", "2020-02-20", "week"),
            ValueError,
            "Invalid date range: end cannot be earlier than start",
        ),
        (
            (None, None, "week"),
            ValueError,
            "At least one of start or end is required",
        ),
    ],
    ids=[
        "test invalid date",
        "test unknown increment",
        "test end date before start date",
        "test no start or end date",
    ],
)
def test_index_date_range_errors(args, error, error_message):
    with pytest.raises(error, match=error_message):
        dataset_date_range(*args)
