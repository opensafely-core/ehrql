import pytest

from ehrql.utils.sequence_utils import get_grouping_level_as_int, ordered_set


@pytest.mark.parametrize(
    "input_list,expected",
    [
        ([4, 3, 2, 3, 5, 5, 2, 2, 1, 4], [4, 3, 2, 5, 1]),
        ([4, -1, 3, 3, 2], [4, -1, 3, 2]),
        (["f", "d", "f", "f", "d", "e", "f"], ["f", "d", "e"]),
        ([1, "d", 2, "d", 3, "d"], [1, "d", 2, 3]),
    ],
)
def test_ordered_set(input_list, expected):
    assert ordered_set(input_list) == expected


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
