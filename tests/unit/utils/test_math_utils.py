import pytest

from ehrql.utils.math_utils import get_grouping_level_as_int, power


@pytest.mark.parametrize(
    "all_groups, group_subset,expected",
    [
        ([], [], 0),
        (["a", "b"], ["a"], 1),
        (["a", "b"], ["b"], 2),
        (["a", "b"], ["a", "b"], 0),
        (["d", "e", "f"], ["d"], 3),
        (["d", "e", "f"], ["f", "d"], 2),
        (["d", "e", "f"], ["d", "f"], 2),
        (["a", "b", "c", "d", "e", "f"], ["a"], 31),
        (["a", "b", "c", "d", "e", "f"], ["a", "b", "c", "d", "e", "f"], 0),
    ],
)
def test_get_grouping_level_as_int(all_groups, group_subset, expected):
    assert get_grouping_level_as_int(all_groups, group_subset) == expected


@pytest.mark.parametrize(
    "lhs,rhs,expected",
    [
        (2, 2, 4),
        (-5, 2, 25),
        (0, 2, 0),
        # zerodivision error
        (0, -2, None),
        # results in complex number
        (-5, 2.5, None),
    ],
)
def test_power(lhs, rhs, expected):
    assert power(lhs, rhs) == expected


def test_power_raises_overflow_error():
    # results in raised OverflowError
    with pytest.raises(OverflowError, match="result out of range"):
        power(10, 500.5)

    # results in overflow error for complex exponentiation, returns None
    assert power(-10, 500.5) is None
