import pytest

from cohortextractor2.query_engines.base_sql import split_list_into_batches


@pytest.mark.parametrize(
    "lst,size,expected",
    [
        ([], 10, []),
        (range(7), 3, [[0, 1, 2], [3, 4, 5], [6]]),
        (range(4), 6, [[0, 1, 2, 3]]),
        (range(12), 4, [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]),
        (range(6), None, [[0, 1, 2, 3, 4, 5]]),
    ],
)
def test_split_list_into_batches(lst, size, expected):
    lst = list(lst)
    results = split_list_into_batches(lst, size)
    results = list(results)
    assert results == expected
