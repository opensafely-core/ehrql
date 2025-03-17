import pytest

from ehrql.utils.math_utils import get_grouping_level_as_int


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
