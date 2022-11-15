import unittest

from databuilder.measures import get_sum_group_by
from databuilder.query_engines.base import BaseQueryEngine


def test_get_sum_group_by():
    population_variable = object()
    value_variable_1 = object()
    value_variable_2 = object()
    group_variable_1 = object()
    group_variable_2 = object()

    N = None
    data = [
        # (patient_id, value_1, value_2, group_1, group_2)
        #
        # Test that NULL values are ignored
        (1, 1, 2, "a", "b"),
        (2, 3, N, "a", "b"),
        (3, N, 4, "a", "b"),
        # Test that another group is formed
        (4, 5, 6, "a", "c"),
        (5, 7, 8, "a", "c"),
        # Test that NULL values in groups are grouped together
        (6, 10, 20, "d", N),
        (7, 30, 40, "d", N),
    ]

    query_engine = unittest.mock.Mock(
        spec=BaseQueryEngine, **{"get_results.return_value": iter(data)}
    )

    results = get_sum_group_by(
        query_engine,
        population_variable,
        [value_variable_1, value_variable_2],
        [group_variable_1, group_variable_2],
    )

    query_engine.get_results.assert_called_with(
        {
            "population": population_variable,
            "value_1": value_variable_1,
            "value_2": value_variable_2,
            "group_1": group_variable_1,
            "group_2": group_variable_2,
        }
    )

    assert results == [
        (1 + 3, 2 + 4, "a", "b"),
        (5 + 7, 6 + 8, "a", "c"),
        (10 + 30, 20 + 40, "d", None),
    ]
