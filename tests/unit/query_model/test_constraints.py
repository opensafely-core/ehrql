from datetime import date

import pytest

from ehrql.tables import Constraint


def test_categorical_validation():
    c = Constraint.Categorical((1, "a"))
    assert c.validate("a")
    assert c.validate(None)
    assert not c.validate("")
    assert not c.validate("b")


def test_not_null_validation():
    c = Constraint.NotNull()
    assert c.validate(1)
    assert not c.validate(None)


def test_unique_validation():
    c = Constraint.Unique()
    assert c.validate(1)


def test_first_of_month_validation():
    c = Constraint.FirstOfMonth()
    assert c.validate(date(2024, 1, 1))
    assert c.validate(None)
    assert not c.validate(date(2024, 1, 2))


def test_regex_validation():
    c = Constraint.Regex("E020[0-9]{5}")
    assert c.validate("E02012345")
    assert c.validate(None)
    assert not c.validate("")
    assert not c.validate("E020")


def test_closed_range_validation():
    c = Constraint.ClosedRange(1, 3)
    assert c.validate(2)
    assert c.validate(None)
    assert not c.validate(0)
    assert not c.validate(4)


def test_general_range_validation():
    assert Constraint.GeneralRange(minimum=1, includes_minimum=True).validate(1)
    assert Constraint.GeneralRange(includes_minimum=True).validate(1)
    assert not Constraint.GeneralRange(minimum=1, includes_minimum=False).validate(1)
    assert Constraint.GeneralRange(maximum=1, includes_maximum=True).validate(1)
    assert Constraint.GeneralRange(includes_maximum=True).validate(1)
    assert not Constraint.GeneralRange(maximum=1, includes_maximum=False).validate(1)

    assert Constraint.GeneralRange(minimum=-1, maximum=1).validate(0)
    assert Constraint.GeneralRange(minimum=-1, maximum=1).validate(None)
    assert not Constraint.GeneralRange(minimum=-1, maximum=1).validate(2)
    assert not Constraint.GeneralRange(minimum=-1, maximum=1).validate(-2)


def test_date_after_instantiation():
    assert Constraint.DateAfter(["some_date"]).column_names == ("some_date",)
    assert Constraint.DateAfter(("some_date",)).column_names == ("some_date",)


def test_date_after_instantiation_with_string_raises_error():
    with pytest.raises(
        TypeError,
        match="'column_names' must be a tuple or list of column names",
    ):
        Constraint.DateAfter("some_date")


def test_date_after_validation():
    assert Constraint.DateAfter(["date"]).validate(date(2024, 1, 1))


def test_general_range_intersect():
    min_1 = Constraint.GeneralRange(minimum=1)
    min_2 = Constraint.GeneralRange(minimum=2)
    min_3 = Constraint.GeneralRange(minimum=3)
    max_3 = Constraint.GeneralRange(maximum=3)
    max_4 = Constraint.GeneralRange(maximum=4)

    range_23 = Constraint.GeneralRange(2, 3)
    range_33 = Constraint.GeneralRange(3, 3)
    range_34 = Constraint.GeneralRange(3, 4)

    assert min_1.intersect(None) == min_1

    assert min_1.intersect(min_2) == min_2.intersect(min_1) == min_2
    assert max_3.intersect(max_4) == max_4.intersect(max_3) == max_3

    assert min_2.intersect(max_3) == max_3.intersect(min_2) == range_23
    assert min_2.intersect(range_23) == range_23.intersect(min_2) == range_23
    assert max_3.intersect(range_23) == range_23.intersect(max_3) == range_23

    assert min_1.intersect(range_23) == range_23.intersect(min_1) == range_23
    assert max_4.intersect(range_23) == range_23.intersect(max_4) == range_23

    assert min_3.intersect(range_23) == range_23.intersect(min_3) == range_33
    assert max_3.intersect(range_34) == range_34.intersect(max_3) == range_33
    assert range_23.intersect(range_34) == range_34.intersect(range_23) == range_33


@pytest.mark.parametrize(
    "constraint",
    [
        Constraint.GeneralRange(minimum=1, includes_minimum=False),
        Constraint.GeneralRange(maximum=1, includes_maximum=False),
        Constraint.GeneralRange(minimum=1, maximum=2, includes_minimum=False),
        Constraint.GeneralRange(minimum=1, maximum=2, includes_maximum=False),
        Constraint.GeneralRange(
            minimum=1, maximum=2, includes_minimum=False, includes_maximum=False
        ),
    ],
)
def test_general_range_intersect_raises_error_if_extremum_not_included(
    constraint,
):
    range_23 = Constraint.GeneralRange(2, 3)

    with pytest.raises(
        NotImplementedError,
        match="Ranges with includes_minimum and/or includes_maximum set to False are not supported yet",
    ):
        constraint.intersect(range_23)

    with pytest.raises(
        NotImplementedError,
        match="Ranges with includes_minimum and/or includes_maximum set to False are not supported yet",
    ):
        range_23.intersect(constraint)
