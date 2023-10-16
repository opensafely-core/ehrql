from datetime import date

from ehrql import maximum_of, minimum_of

from ..tables import p


title = "Minimum and maximum aggregations across Patient series"

table_data = {
    p: """
          |  i1 |  i2 |     d1     |     d2     | s1 | s2 |  f1  |  f2
        --+-----+-----|------------|------------|----|----|------|------
        1 | 101 | 112 | 2001-01-01 | 2012-12-12 | a  | d  | 1.01 | 1.12
        2 |     | 211 |            | 2021-01-01 |    | f  |      | 2.11
        3 |     |     |            |            |    |    |      |
    """,
}


def test_maximum_of_two_integer_patient_series(spec_test):
    spec_test(
        table_data,
        maximum_of(p.i1, p.i2),
        {
            1: 112,
            2: 211,
            3: None,
        },
    )


def test_minimum_of_two_integer_patient_series(spec_test):
    spec_test(
        table_data,
        minimum_of(p.i1, p.i2),
        {
            1: 101,
            2: 211,
            3: None,
        },
    )


def test_minimum_of_two_integer_patient_series_and_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(p.i1, p.i2, 150),
        {
            1: 101,
            2: 150,
            3: 150,
        },
    )


def test_maximum_of_two_integer_patient_series_and_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(p.i1, p.i2, 150),
        {
            1: 150,
            2: 211,
            3: 150,
        },
    )


def test_minimum_of_two_date_patient_series(spec_test):
    spec_test(
        table_data,
        minimum_of(p.d1, p.d2),
        {
            1: date(2001, 1, 1),
            2: date(2021, 1, 1),
            3: None,
        },
    )


def test_maximum_of_two_date_patient_series(spec_test):
    spec_test(
        table_data,
        maximum_of(p.d1, p.d2),
        {
            1: date(2012, 12, 12),
            2: date(2021, 1, 1),
            3: None,
        },
    )


def test_minimum_of_two_date_patient_series_and_datetime_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(p.d1, p.d2, date(2015, 5, 5)),
        {
            1: date(2001, 1, 1),
            2: date(2015, 5, 5),
            3: date(2015, 5, 5),
        },
    )


def test_maximum_of_two_date_patient_series_and_datetime_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(p.d1, p.d2, date(2015, 5, 5)),
        {
            1: date(2015, 5, 5),
            2: date(2021, 1, 1),
            3: date(2015, 5, 5),
        },
    )


def test_minimum_of_two_date_patient_series_and_string_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(p.d1, p.d2, "2015-05-05"),
        {
            1: date(2001, 1, 1),
            2: date(2015, 5, 5),
            3: date(2015, 5, 5),
        },
    )


def test_maximum_of_two_date_patient_series_and_string_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(p.d1, p.d2, "2015-05-05"),
        {
            1: date(2015, 5, 5),
            2: date(2021, 1, 1),
            3: date(2015, 5, 5),
        },
    )


def test_maximum_of_two_float_patient_series(spec_test):
    spec_test(
        table_data,
        maximum_of(p.f1, p.f2),
        {
            1: 1.12,
            2: 2.11,
            3: None,
        },
    )


def test_minimum_of_two_float_patient_series(spec_test):
    spec_test(
        table_data,
        minimum_of(p.f1, p.f2),
        {
            1: 1.01,
            2: 2.11,
            3: None,
        },
    )


def test_minimum_of_two_float_patient_series_and_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(p.f1, p.f2, 1.5),
        {
            1: 1.01,
            2: 1.5,
            3: 1.5,
        },
    )


def test_maximum_of_two_float_patient_series_and_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(p.f1, p.f2, 1.5),
        {
            1: 1.5,
            2: 2.11,
            3: 1.5,
        },
    )


def test_maximum_of_two_string_patient_series(spec_test):
    spec_test(
        table_data,
        maximum_of(p.s1, p.s2),
        {
            1: "d",
            2: "f",
            3: None,
        },
    )


def test_minimum_of_two_string_patient_series(spec_test):
    spec_test(
        table_data,
        minimum_of(p.s1, p.s2),
        {
            1: "a",
            2: "f",
            3: None,
        },
    )


def test_minimum_of_two_string_patient_series_and_a_value(spec_test):
    spec_test(
        table_data,
        minimum_of(p.s1, p.s2, "e"),
        {
            1: "a",
            2: "e",
            3: "e",
        },
    )


def test_maximum_of_two_string_patient_series_and_a_value(spec_test):
    spec_test(
        table_data,
        maximum_of(p.s1, p.s2, "e"),
        {
            1: "e",
            2: "f",
            3: "e",
        },
    )


def test_maximum_of_two_integers_all_a_values(spec_test):
    spec_test(
        table_data,
        maximum_of(1, 2, 3),
        {
            1: 3,
            2: 3,
            3: 3,
        },
    )
