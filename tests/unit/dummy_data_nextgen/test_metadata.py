from ehrql import Dataset
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator
from ehrql.tables.core import patients
from ehrql.tables.tpp import (
    addresses,
)


def test_dummy_data_generator_generates_addresses_end_date_after_start_date():
    dataset = Dataset()
    dataset.define_population(patients.exists_for_patient())

    last_address = addresses.sort_by(addresses.start_date).last_for_patient()
    dataset.is_valid = last_address.start_date <= last_address.end_date

    variable_definitions = dataset._compile()
    generator = DummyDataGenerator(variable_definitions)
    generator.population_size = 10
    generator.batch_size = 5
    results = list(generator.get_results())

    assert set(r.is_valid for r in results).issubset({True, None})
