import re
from datetime import date

import pytest

from ehrql import Error, Measures, months
from ehrql.measures.measures import Measure, create_measures
from ehrql.tables import PatientFrame, Series, table


@table
class patients(PatientFrame):
    is_interesting = Series(bool)
    score = Series(int)
    category = Series(str)
    style = Series(str)


def test_create_measures():
    assert isinstance(create_measures(), Measures)


def test_define_measures():
    intervals = [
        (date(2021, 1, 1), date(2021, 1, 31)),
        (date(2021, 2, 1), date(2021, 2, 28)),
    ]

    measures = Measures()

    measures.define_defaults(
        numerator=patients.score,
        denominator=patients.is_interesting,
        intervals=intervals,
    )

    measures.define_measure(
        name="test_1",
        group_by={"category": patients.category},
    )
    measures.define_measure(
        name="test_2",
        group_by={"style": patients.style},
    )

    assert measures.disclosure_control_config.enabled

    assert len(measures) == 2

    assert list(measures) == [
        Measure(
            name="test_1",
            numerator=patients.score._qm_node,
            denominator=patients.is_interesting._qm_node,
            group_by={
                "category": patients.category._qm_node,
            },
            intervals=tuple(intervals),
        ),
        Measure(
            name="test_2",
            numerator=patients.score._qm_node,
            denominator=patients.is_interesting._qm_node,
            group_by={
                "style": patients.style._qm_node,
            },
            intervals=tuple(intervals),
        ),
    ]


def test_define_measures_with_default_group_by():
    # Regression test for #1423.

    intervals = [
        (date(2021, 1, 1), date(2021, 1, 31)),
        (date(2021, 2, 1), date(2021, 2, 28)),
    ]

    measures = Measures()

    measures.define_defaults(
        numerator=patients.score,
        denominator=patients.is_interesting,
        intervals=intervals,
        group_by={"category": patients.category},
    )

    measures.define_measure(
        name="test_1",
    )
    measures.define_measure(
        name="test_2",
    )

    assert measures.disclosure_control_config.enabled

    assert len(measures) == 2

    assert list(measures) == [
        Measure(
            name="test_1",
            numerator=patients.score._qm_node,
            denominator=patients.is_interesting._qm_node,
            group_by={
                "category": patients.category._qm_node,
            },
            intervals=tuple(intervals),
        ),
        Measure(
            name="test_2",
            numerator=patients.score._qm_node,
            denominator=patients.is_interesting._qm_node,
            group_by={
                "category": patients.category._qm_node,
            },
            intervals=tuple(intervals),
        ),
    ]


def test_cannot_redefine_defaults():
    measures = Measures()
    measures.define_defaults(numerator=patients.score)
    with pytest.raises(Error, match="Defaults already set"):
        measures.define_defaults(numerator=patients.is_interesting)


def test_must_define_all_attributes():
    measures = Measures()
    measures.define_defaults(numerator=patients.score)
    with pytest.raises(
        Error,
        match="No value supplied for 'intervals' and no default defined",
    ):
        measures.define_measure(
            name="test",
            denominator=patients.is_interesting,
        )


def test_names_must_be_unique():
    measures = Measures()

    measures.define_defaults(
        denominator=patients.is_interesting,
        intervals=[(date(2021, 1, 1), date(2021, 1, 31))],
        group_by={"category": patients.category},
    )

    measures.define_measure(name="test", numerator=patients.score)
    with pytest.raises(Error, match="Measure already defined with name: test"):
        measures.define_measure(name="test", numerator=patients.is_interesting)


@pytest.mark.parametrize(
    "name",
    [
        "",
        "12346No Spaces",
        "No-Dashes",
    ],
)
def test_names_must_be_valid(name):
    measures = Measures()
    with pytest.raises(
        Error,
        match=(
            "must start with a letter and contain only alphanumeric characters"
            " and underscores"
        ),
    ):
        measures.define_measure(
            name=name,
            numerator=patients.score,
            denominator=patients.is_interesting,
            intervals=[(date(2021, 1, 1), date(2021, 1, 31))],
            group_by={"category": patients.category},
        )


def test_group_by_columns_must_be_consistent():
    measures = Measures()

    measures.define_defaults(
        numerator=patients.score,
        denominator=patients.is_interesting,
        intervals=[(date(2021, 1, 1), date(2021, 1, 31))],
    )

    measures.define_measure(
        name="test_1",
        group_by={
            "style": patients.style,
            "category": patients.category,
        },
    )
    with pytest.raises(
        Error, match="Inconsistent definition for `group_by` column: category"
    ):
        measures.define_measure(
            name="test_2",
            group_by={
                "style": patients.style,
                "category": patients.is_interesting,
            },
        )


def test_numerator_must_be_patient_series():
    measures = Measures()

    with pytest.raises(
        TypeError,
        match="invalid numerator:\nExpecting an ehrQL series, got type 'object'",
    ):
        measures.define_measure(
            name="test",
            numerator=object(),
            denominator=patients.is_interesting,
            intervals=[(date(2021, 1, 1), date(2021, 1, 31))],
            group_by={"category": patients.category},
        )


def test_denominator_must_be_int_or_bool_series():
    measures = Measures()

    with pytest.raises(
        TypeError,
        match=(
            "invalid denominator:\n"
            "Expecting a boolean or integer series, got series of type 'str'"
        ),
    ):
        measures.define_measure(
            name="test",
            numerator=patients.score,
            denominator=patients.style,
            intervals=[(date(2021, 1, 1), date(2021, 1, 31))],
            group_by={"category": patients.category},
        )


@pytest.mark.parametrize(
    "group_by,error",
    [
        (1234, "`group_by` must be a dictionary"),
        ({1234: patients.category}, "group_by` names must be strings"),
        ({"My Group": patients.category}, "alphanumeric characters and underscores"),
        ({"measure": patients.category}, "disallowed `group_by` column name: measure"),
        (
            {"my_group": 1234},
            "invalid `group_by` value for 'my_group':\n"
            "Expecting an ehrQL series, got type 'int'",
        ),
    ],
)
def test_invalid_group_by_is_rejected(group_by, error):
    measures = Measures()

    with pytest.raises((TypeError, Error), match=error):
        measures.define_measure(
            name="test",
            numerator=patients.score,
            denominator=patients.is_interesting,
            intervals=[(date(2021, 1, 1), date(2021, 1, 31))],
            group_by=group_by,
        )


@pytest.mark.parametrize(
    "intervals,error",
    [
        (object(), "`intervals` must be a list"),
        ([(1, 2)], "`intervals` must contain pairs of dates"),
        ([(date(2020, 1, 1),)], "`intervals` must contain pairs of dates"),
        ([(date(2021, 1, 1), date(2020, 1, 1))], "start date must be before end date"),
        (
            months(12),
            re.escape(
                "You must supply a date using `months(value=12).starting_on('<DATE>')`"
                " or `months(value=12).ending_on('<DATE>')`"
            ),
        ),
    ],
)
def test_invalid_intervals_are_rejected(intervals, error):
    measures = Measures()

    with pytest.raises(Error, match=error):
        measures.define_measure(
            name="test",
            numerator=patients.score,
            denominator=patients.is_interesting,
            intervals=intervals,
            group_by={"category": patients.category},
        )


def test_configure_disclosure_control():
    measures = Measures()
    measures.configure_disclosure_control(enabled=False)
    assert not measures.disclosure_control_config.enabled
