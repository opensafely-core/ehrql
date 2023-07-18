from datetime import date

from ehrql import maximum_of, minimum_of

from ..tables import e


title = "Minimum and maximum aggregations across Event series"


table_data = {
    e: """
          |  i1 |  i2 |     d1     |     d2     | s1 | s2 |  f1  |  f2
        --+-----+-----|------------|------------|----|----|------|------
        1 | 101 | 111 | 2001-01-01 | 2002-02-02 | a  | b  | 1.01 | 1.11
        1 | 102 | 112 | 2011-11-11 | 2012-12-12 | c  | d  | 1.02 | 1.12
        2 |     | 211 |            | 2021-01-01 |    | f  |      | 2.11
        3 |     |     |            |            |    |    |      |
    """,
}


def test_maximum_of_two_integer_event_series(spec_test):
    spec_test(
        table_data,
        maximum_of(e.i1, e.i2).maximum_for_patient(),
        {
            1: 112,
            2: 211,
            3: None,
        },
    )


def test_minimum_of_two_integer_event_series(spec_test):
    spec_test(
        table_data,
        minimum_of(e.i1, e.i2).minimum_for_patient(),
        {
            1: 101,
            2: 211,
            3: None,
        },
    )


def test_minimum_of_two_integer_event_series_and_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(e.i1, e.i2, 150).minimum_for_patient(),
        {
            1: 101,
            2: 150,
            3: 150,
        },
    )


def test_maximum_of_two_integer_event_series_and_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(e.i1, e.i2, 150).maximum_for_patient(),
        {
            1: 150,
            2: 211,
            3: 150,
        },
    )


def test_minimum_of_two_date_event_series(spec_test):
    spec_test(
        table_data,
        minimum_of(e.d1, e.d2).minimum_for_patient(),
        {
            1: date(2001, 1, 1),
            2: date(2021, 1, 1),
            3: None,
        },
    )


def test_maximum_of_two_date_event_series(spec_test):
    spec_test(
        table_data,
        maximum_of(e.d1, e.d2).maximum_for_patient(),
        {
            1: date(2012, 12, 12),
            2: date(2021, 1, 1),
            3: None,
        },
    )


def test_minimum_of_two_date_event_series_and_datetime_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(e.d1, e.d2, date(2015, 5, 5)).minimum_for_patient(),
        {
            1: date(2001, 1, 1),
            2: date(2015, 5, 5),
            3: date(2015, 5, 5),
        },
    )


def test_maximum_of_two_date_event_series_and_datetime_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(e.d1, e.d2, date(2015, 5, 5)).maximum_for_patient(),
        {
            1: date(2015, 5, 5),
            2: date(2021, 1, 1),
            3: date(2015, 5, 5),
        },
    )


def test_minimum_of_two_date_event_series_and_string_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(e.d1, e.d2, "2015-05-05").minimum_for_patient(),
        {
            1: date(2001, 1, 1),
            2: date(2015, 5, 5),
            3: date(2015, 5, 5),
        },
    )


def test_maximum_of_two_date_event_series_and_string_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(e.d1, e.d2, "2015-05-05").maximum_for_patient(),
        {
            1: date(2015, 5, 5),
            2: date(2021, 1, 1),
            3: date(2015, 5, 5),
        },
    )


def test_maximum_of_two_float_event_series(spec_test):
    spec_test(
        table_data,
        maximum_of(e.f1, e.f2).maximum_for_patient(),
        {
            1: 1.12,
            2: 2.11,
            3: None,
        },
    )


def test_minimum_of_two_float_event_series(spec_test):
    spec_test(
        table_data,
        minimum_of(e.f1, e.f2).minimum_for_patient(),
        {
            1: 1.01,
            2: 2.11,
            3: None,
        },
    )


def test_minimum_of_two_float_event_series_and_float_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(e.f1, e.f2, 1.5).minimum_for_patient(),
        {
            1: 1.01,
            2: 1.5,
            3: 1.5,
        },
    )


def test_maximum_of_two_float_event_series_and_float_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(e.f1, e.f2, 1.5).maximum_for_patient(),
        {
            1: 1.5,
            2: 2.11,
            3: 1.5,
        },
    )


def test_minimum_of_two_float_event_series_and_integer_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(e.f1, e.f2, 2).minimum_for_patient(),
        {
            1: 1.01,
            2: 2,
            3: 2,
        },
    )


def test_maximum_of_two_float_event_series_and_integer_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(e.f1, e.f2, 2).maximum_for_patient(),
        {
            1: 2,
            2: 2.11,
            3: 2,
        },
    )


def test_maximum_of_two_string_event_series(spec_test):
    spec_test(
        table_data,
        maximum_of(e.s1, e.s2).maximum_for_patient(),
        {
            1: "d",
            2: "f",
            3: None,
        },
    )


def test_minimum_of_two_string_event_series(spec_test):
    spec_test(
        table_data,
        minimum_of(e.s1, e.s2).minimum_for_patient(),
        {
            1: "a",
            2: "f",
            3: None,
        },
    )


def test_minimum_of_two_string_event_series_and_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(e.s1, e.s2, "e").minimum_for_patient(),
        {
            1: "a",
            2: "e",
            3: "e",
        },
    )


def test_maximum_of_two_string_event_series_and_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(e.s1, e.s2, "e").maximum_for_patient(),
        {
            1: "e",
            2: "f",
            3: "e",
        },
    )


def test_maximum_of_nested_aggregate(spec_test):
    spec_test(
        table_data,
        maximum_of(
            e.s1.count_distinct_for_patient(),
            e.s2.count_distinct_for_patient(),
        ),
        {
            1: 2,
            2: 1,
            3: 0,
        },
    )


def test_maximum_of_nested_aggregate_and_column_and_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(e.s1.count_distinct_for_patient(), e.i1, 1).maximum_for_patient(),
        {
            1: 102,
            2: 1,
            3: 1,
        },
    )
