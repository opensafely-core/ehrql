from datetime import date
from unittest import mock

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from ehrql import create_dataset, years
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator
from ehrql.query_language import compile
from ehrql.tables.core import patients


@pytest.mark.parametrize("sex", ["male", "female", "intersex"])
@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_can_generate_single_sex_data_in_one_shot(patched_time, sex):
    dataset = create_dataset()

    dataset.define_population(patients.sex == sex)

    target_size = 1000

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after one loop pass, as we
    # should be able to generate these correctly in the first pass.
    patched_time.time.side_effect = [0.0, 20.0]
    data = generator.get_data()

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Within that table expecting we generated a full population
    assert len(data_for_table) == target_size


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_can_generate_patients_from_a_specific_year(patched_time):
    dataset = create_dataset()

    dataset.define_population(patients.date_of_birth.year == 1950)

    target_size = 1000

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after one loop pass, as we
    # should be able to generate these correctly in the first pass.
    patched_time.time.side_effect = [0.0, 20.0]
    data = generator.get_data()

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Within that table expecting we generated a full population
    assert len(data_for_table) == target_size


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_can_combine_constraints_on_generated_data(patched_time):
    dataset = create_dataset()

    dataset.define_population(
        (patients.date_of_birth.year == 1970) & (patients.sex == "intersex")
    )

    target_size = 1000

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after one loop pass, as we
    # should be able to generate these correctly in the first pass.
    patched_time.time.side_effect = [0.0, 20.0]
    data = generator.get_data()

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Within that table expecting we generated a full population
    assert len(data_for_table) == target_size


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_will_satisfy_constraints_on_both_sides_of_an_or(patched_time):
    dataset = create_dataset()

    dataset.define_population(
        ((patients.date_of_birth.year == 1970) & (patients.sex == "male"))
        | ((patients.date_of_birth.year == 1963) & (patients.sex == "male"))
    )

    target_size = 1000

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after one loop pass, as we
    # should be able to generate these correctly in the first pass.
    patched_time.time.side_effect = [0.0, 20.0]
    data = generator.get_data()

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Within that table expecting we generated a full population
    assert len(data_for_table) > 0


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_basic_patient_constraints_age_and_sex(patched_time):
    index_date = "2023-10-01"

    dataset = create_dataset()

    is_female_or_male = patients.sex.is_in(["female", "male"])

    was_adult = (patients.age_on(index_date) >= 18) & (
        patients.age_on(index_date) <= 110
    )

    was_alive = (
        patients.date_of_death.is_after(index_date) | patients.date_of_death.is_null()
    )

    dataset.define_population(is_female_or_male & was_adult & was_alive)

    target_size = 1000

    dataset.age = patients.age_on(index_date)
    dataset.sex = patients.sex

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after three loop passes.
    # We cannot currently generate the exact data reliably because the
    # constraint on date of death doesn't straightforwardly map to a
    # single logical constraint.
    patched_time.time.side_effect = [0.0, 1.0, 2.0, 20.0]
    data = generator.get_data()

    (data_for_table,) = (v for k, v in data.items() if k.name == "patients")
    # Within that table expecting we generated a full population
    assert len(data_for_table) == target_size


@st.composite
def birthday_range_query(draw):
    # We generate a single date that we require to be valid for
    # our query as a way of ensuring that the query always has
    # results.

    reasonable_dates = st.dates(min_value=date(1900, 1, 1), max_value=date(2024, 9, 1))
    valid_date = draw(reasonable_dates).replace(month=1)

    query_endpoints = draw(st.lists(reasonable_dates, min_size=1))
    query_components = []

    for endpoint in query_endpoints:
        # NB draw unconditionally for easier shrinking, but need
        # to force equality to be allowed if this is equal to the
        # target date. We invert it so that it shrinks to allowing
        # equality, as this is the slightly simpler codepath.
        allow_equal = not draw(st.booleans())
        if endpoint == valid_date:
            allow_equal = True
        if endpoint >= valid_date:
            if allow_equal:
                query_components.append(patients.date_of_birth <= endpoint)
            else:
                query_components.append(patients.date_of_birth < endpoint)
        else:
            if allow_equal:
                query_components.append(patients.date_of_birth >= endpoint)
            else:
                query_components.append(patients.date_of_birth > endpoint)
    while len(query_components) > 1:
        q = query_components.pop()
        i = draw(st.integers(0, len(query_components) - 1))
        query_components[i] &= q
    return query_components[0]


@example(query=patients.date_of_birth < date(1900, 12, 31), target_size=1000)
@example(query=patients.date_of_birth >= date(1900, 1, 2), target_size=1000)
@settings(deadline=None)
@given(query=birthday_range_query(), target_size=st.integers(1, 1000))
@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_combined_age_range_in_one_shot(patched_time, query, target_size):
    dataset = create_dataset()

    dataset = create_dataset()

    dataset.define_population(query)

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after one loop pass, as we
    # should be able to generate these correctly in the first pass.
    patched_time.time.side_effect = [0.0, 20.0]
    data = generator.get_data()

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Within that table expecting we generated a full population
    assert len(data_for_table) == target_size


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_date_arithmetic_comparison(patched_time):
    dataset = create_dataset()

    index_date = date(2022, 3, 1)
    died_more_than_10_years_ago = (patients.date_of_death + years(10)) < index_date
    dataset.define_population(died_more_than_10_years_ago)
    dataset.date_of_birth = patients.date_of_birth
    dataset.date_of_death = patients.date_of_death

    target_size = 1000

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after one loop pass, as we
    # should be able to generate these correctly in the first pass.
    patched_time.time.side_effect = [0.0, 20.0]
    data = generator.get_data()

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Confirm that all patients have date of birth before date of death
    assert all(row[1] <= row[2] for row in data_for_table)
    # Within that table expecting we generated a full population
    assert len(data_for_table) == target_size
