from datetime import date

import pytest

from ehrql.utils.date_utils import (
    date_add_months,
    date_add_weeks,
    date_add_years,
    generate_intervals,
)


@pytest.mark.parametrize(
    "start_date,n,expected",
    [
        (
            date(2020, 2, 20),
            3,
            [
                (date(2020, 2, 20), date(2020, 2, 26)),
                (date(2020, 2, 27), date(2020, 3, 4)),
                (date(2020, 3, 5), date(2020, 3, 11)),
            ],
        ),
        (
            date(2020, 3, 5),
            -3,
            [
                (date(2020, 2, 20), date(2020, 2, 26)),
                (date(2020, 2, 27), date(2020, 3, 4)),
                (date(2020, 3, 5), date(2020, 3, 11)),
            ],
        ),
    ],
)
def test_generate_intervals_weeks(start_date, n, expected):
    assert generate_intervals(date_add_weeks, start_date, n) == expected


@pytest.mark.parametrize(
    "start_date,n,expected",
    [
        (
            date(2020, 11, 1),
            3,
            [
                (date(2020, 11, 1), date(2020, 11, 30)),
                (date(2020, 12, 1), date(2020, 12, 31)),
                (date(2021, 1, 1), date(2021, 1, 31)),
            ],
        ),
        (
            date(2021, 1, 1),
            -3,
            [
                (date(2020, 11, 1), date(2020, 11, 30)),
                (date(2020, 12, 1), date(2020, 12, 31)),
                (date(2021, 1, 1), date(2021, 1, 31)),
            ],
        ),
    ],
)
def test_generate_intervals_months(start_date, n, expected):
    assert generate_intervals(date_add_months, start_date, n) == expected


@pytest.mark.parametrize(
    "start_date,n,expected",
    [
        (
            date(2020, 11, 1),
            3,
            [
                (date(2020, 11, 1), date(2021, 10, 31)),
                (date(2021, 11, 1), date(2022, 10, 31)),
                (date(2022, 11, 1), date(2023, 10, 31)),
            ],
        ),
        (
            date(2022, 11, 1),
            -3,
            [
                (date(2020, 11, 1), date(2021, 10, 31)),
                (date(2021, 11, 1), date(2022, 10, 31)),
                (date(2022, 11, 1), date(2023, 10, 31)),
            ],
        ),
    ],
)
def test_generate_intervals_years(start_date, n, expected):
    assert generate_intervals(date_add_years, start_date, n) == expected
