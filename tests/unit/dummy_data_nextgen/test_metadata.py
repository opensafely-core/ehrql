from ehrql import Dataset
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator
from ehrql.tables.core import practice_registrations


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
