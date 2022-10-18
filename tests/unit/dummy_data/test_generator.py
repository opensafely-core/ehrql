import datetime

import pytest

from databuilder.dummy_data.generator import DummyDataGenerator
from databuilder.dummy_data.query_info import ColumnInfo
from databuilder.ehrql import Dataset
from databuilder.query_language import compile
from databuilder.tables import (
    CategoricalConstraint,
    EventFrame,
    PatientFrame,
    Series,
    table,
)


@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)
    date_of_death = Series(datetime.date)
    sex = Series(str, constraints=[CategoricalConstraint("male", "female", "intersex")])


@table
class practice_registrations(EventFrame):
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    practice_id = Series(int)


@table
class events(EventFrame):
    date = Series(datetime.date)
    code = Series(str)


def test_dummy_data_generator():
    # Define a basic dataset
    dataset = Dataset()
    dataset.set_population(practice_registrations.exists_for_patient())
    dataset.date_of_birth = patients.date_of_birth
    dataset.date_of_death = patients.date_of_death
    dataset.sex = patients.sex

    last_event = (
        events.take(events.code.is_in(["abc", "def"]))
        .sort_by(events.date)
        .last_for_patient()
    )
    dataset.code = last_event.code
    dataset.date = last_event.date

    # Generate some results
    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions)
    generator.population_size = 7
    generator.batch_size = 4
    results = list(generator.get_results())

    # Check they look right
    assert len(results) == 7

    for r in results:
        assert isinstance(r.date_of_birth, datetime.date)
        assert r.date_of_death is None or r.date_of_death > r.date_of_birth
        assert r.sex in {"male", "female", "intersex"}
        # To get full coverage here we need to generate enough data so that we get at
        # least one patient with a matching event and one without
        if r.code is not None or r.date is not None:
            assert r.code in {"abc", "def"}
            assert isinstance(r.date, datetime.date)


@pytest.mark.parametrize("type_", [bool, int, float, str, datetime.date])
def test_get_random_value(generator, type_):
    column_info = ColumnInfo(name="test", categories=None, type=type_)
    value = generator.get_random_value(column_info)
    assert isinstance(value, type_)


@pytest.fixture(scope="module")
def generator():
    dataset = Dataset()
    dataset.set_population(patients.exists_for_patient())
    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions)
    generator.generate_patient_facts()
    return generator
