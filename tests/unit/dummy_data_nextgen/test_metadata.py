import pytest

from ehrql import Dataset
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator
from ehrql.dummy_data_nextgen.metadata import DummyDataConstraint
from ehrql.tables.core import practice_registrations
from ehrql.tables.tpp import (
    addresses,
)


class TestRelatedToOther:
    def test_description(self):
        constraint = DummyDataConstraint.RelatedToOther("other_column", ">=")
        assert (
            constraint.description == "Value must be >= value in column `other_column`"
        )

    @pytest.mark.parametrize(
        "relation,value,other_value,expected",
        [
            ("==", None, None, True),
            ("==", None, 1, True),
            ("==", 1, None, True),
            ("<", 1, 2, True),
            ("<", 2, 1, False),
            ("<=", 1, 2, True),
            ("<=", 2, 2, True),
            ("<=", 2, 1, False),
            ("==", 1, 1, True),
            ("==", 1, 2, False),
            ("!=", 1, 2, True),
            ("!=", 1, 1, False),
            (">=", 2, 1, True),
            (">=", 2, 2, True),
            (">=", 1, 2, False),
            (">", 2, 1, True),
            (">", 1, 2, False),
        ],
    )
    def test_validate(self, relation, value, other_value, expected):
        constraint = DummyDataConstraint.RelatedToOther("other_column", relation)
        assert constraint.validate(value, other_value) == expected

    def test_validate_with_unknown_relation(self):
        constraint = DummyDataConstraint.RelatedToOther("other_column", "unknown")
        with pytest.raises(AssertionError, match="Unknown relation 'unknown'"):
            constraint.validate(1, 2)

    @pytest.mark.parametrize(
        "relation,other_value,values,expected_result",
        [
            ("==", 2, [], []),
            ("<=", 2, [1, 2, 3], [1, 2]),
            ("<=", 2, [3, 4], []),
            ("<", 2, [1, 2, 3], [1]),
            ("<", 2, [2, 3], []),
            (">=", 2, [1, 2, 3], [2, 3]),
            (">=", 2, [1], []),
            (">", 2, [1, 2, 3], [3]),
            (">", 2, [1, 2], []),
            ("==", 2, [1, 2, 3], [2]),
            ("==", 2, [1, 3], []),
            ("!=", 2, [1, 2, 3], [1, 3]),
            ("!=", 2, [2], []),
        ],
    )
    def test_filter_values(self, relation, other_value, values, expected_result):
        constraint = DummyDataConstraint.RelatedToOther("other_column", relation)
        assert constraint.filter_values(values, other_value) == expected_result
        assert constraint.filter_values([None] + values, other_value) == (
            [None] + expected_result
        )


def test_dummy_data_generator_only_generates_positive_practice_pseudo_id_up_to_999():
    dataset = Dataset()
    dataset.define_population(practice_registrations.exists_for_patient())

    smallest_id = practice_registrations.practice_pseudo_id.minimum_for_patient()
    largest_id = practice_registrations.practice_pseudo_id.maximum_for_patient()
    dataset.is_valid = (smallest_id >= 0) & (largest_id <= 999)

    variable_definitions = dataset._compile()
    generator = DummyDataGenerator(variable_definitions)
    generator.population_size = 10
    generator.batch_size = 5
    results = set(generator.get_results())

    assert set(r.is_valid for r in results) == {True}


@pytest.mark.parametrize(
    "table,earlier_date_col_name,later_date_col_name",
    [
        (addresses, "start_date", "end_date"),
    ],
)
def test_dummy_data_generator_with_one_date_constrained_to_be_before_another(
    table, earlier_date_col_name, later_date_col_name
):
    dataset = Dataset()
    dataset.define_population(table.exists_for_patient())

    last_event = table.sort_by(getattr(table, earlier_date_col_name)).last_for_patient()
    last_event_earlier_date = getattr(last_event, earlier_date_col_name)
    last_event_later_date = getattr(last_event, later_date_col_name)
    dataset.is_valid = last_event_earlier_date <= last_event_later_date

    variable_definitions = dataset._compile()
    generator = DummyDataGenerator(variable_definitions)
    generator.population_size = 10
    generator.batch_size = 5
    results = list(generator.get_results())

    # We might want to mix in some invalid results in the future?
    assert set(r.is_valid for r in results).issubset({True, None})
