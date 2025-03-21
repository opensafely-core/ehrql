import pytest

from ehrql.utils.sequence_utils import ordered_set


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
