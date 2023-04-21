import datetime
import re
from unittest import mock

import pytest

from ehrql.dummy_data.generator import DummyDataGenerator, DummyPatientGenerator
from ehrql.dummy_data.query_info import ColumnInfo, TableInfo
from ehrql import Dataset
from ehrql.query_language import compile
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date, constraints=[Constraint.FirstOfMonth()])
    date_of_death = Series(datetime.date)
    sex = Series(
        str, constraints=[Constraint.Categorical(["male", "female", "intersex"])]
    )


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
    dataset.define_population(practice_registrations.exists_for_patient())
    dataset.date_of_birth = patients.date_of_birth
    dataset.date_of_death = patients.date_of_death
    dataset.sex = patients.sex

    last_event = (
        events.where(events.code.is_in(["abc", "def"]))
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
        assert r.date_of_birth.day == 1
        assert r.date_of_death is None or r.date_of_death > r.date_of_birth
        assert r.sex in {"male", "female", "intersex"}
        # To get full coverage here we need to generate enough data so that we get at
        # least one patient with a matching event and one without
        if r.code is not None or r.date is not None:
            assert r.code in {"abc", "def"}
            assert isinstance(r.date, datetime.date)


@mock.patch("ehrql.dummy_data.generator.time")
def test_dummy_data_generator_timeout_with_some_results(patched_time):
    dataset = Dataset()
    dataset.define_population(patients.exists_for_patient())

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions)
    generator.population_size = 100
    generator.batch_size = 3
    generator.timeout = 10

    # Configure `time.time()` so we timeout after two loop passes
    patched_time.time.side_effect = [0.0, 5.0, 20.0]
    data = generator.get_data()

    # Expecting 2 loops * 3 patients * 1 table
    assert len(data) == 6


@mock.patch("ehrql.dummy_data.generator.time")
def test_dummy_data_generator_timeout_with_no_results(patched_time):
    # Define a dataset with a condition no patient can match
    dataset = Dataset()
    dataset.define_population(patients.sex != patients.sex)

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions)
    generator.timeout = 10

    # Configure `time.time` so we timeout immediately
    patched_time.time.side_effect = [0.0, 100.0]
    data = generator.get_data()

    # Expecting 1 patient * 1 table
    assert len(data) == 1


@pytest.mark.parametrize("type_", [bool, int, float, str, datetime.date])
def test_dummy_patient_generator_get_random_value(dummy_patient_generator, type_):
    column_info = ColumnInfo(name="test", type=type_)
    value = dummy_patient_generator.get_random_value(column_info)
    assert isinstance(value, type_)


def test_get_random_value_on_first_of_month(dummy_patient_generator):
    column_info = ColumnInfo(
        name="test",
        type=datetime.date,
        constraints=(Constraint.FirstOfMonth(),),
    )
    values = [dummy_patient_generator.get_random_value(column_info) for _ in range(100)]
    assert len(set(values)) > 1, "dates are all identical"
    assert all(value.day == 1 for value in values)


def test_get_random_str(dummy_patient_generator):
    column_info = ColumnInfo(name="test", type=str)
    values = [dummy_patient_generator.get_random_value(column_info) for _ in range(10)]
    lengths = {len(s) for s in values}
    assert len(lengths) > 1, "strings are all the same length"


def test_get_random_str_with_regex(dummy_patient_generator):
    column_info = ColumnInfo(
        name="test",
        type=str,
        constraints=(Constraint.Regex("AB[X-Z]{5}"),),
    )
    values = [dummy_patient_generator.get_random_value(column_info) for _ in range(10)]
    assert len(set(values)) > 1, "strings are all identical"
    assert all(re.match(r"AB[X-Z]{5}", value) for value in values)


def test_rows_for_patients_with_first_of_month_constraint(dummy_patient_generator):
    table_info = TableInfo(
        name="patients",
        has_one_row_per_patient=True,
        columns={
            # No `FirstOfMonth` constraint applied to non-nullable `date_of_birth`
            "date_of_birth": ColumnInfo("date_of_birth", datetime.date, constraints=()),
            # `FirstOfMonth` constraint applied to nullable `date_of_death`
            "date_of_death": ColumnInfo(
                "date_of_death", datetime.date, constraints=(Constraint.FirstOfMonth(),)
            ),
        },
    )
    rows = []
    for _ in range(10):
        dummy_patient_generator.generate_patient_facts()
        rows.extend(dummy_patient_generator.rows_for_patients(table_info))
    assert len(rows) == 10
    # Assert constraints are respected
    assert all(r["date_of_birth"] is not None for r in rows)
    assert any(r["date_of_birth"].day != 1 for r in rows)  # pragma: no branch
    assert all(r["date_of_death"] is None or r["date_of_death"].day == 1 for r in rows)


@pytest.fixture(scope="module")
def dummy_patient_generator():
    dataset = Dataset()
    dataset.define_population(patients.exists_for_patient())
    variable_definitions = compile(dataset)
    generator = DummyPatientGenerator(variable_definitions, random_seed="abc")
    generator.generate_patient_facts()
    return generator
