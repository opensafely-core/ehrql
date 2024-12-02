import operator
from datetime import date
from unittest import mock

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from hypothesis.vendor.pretty import pretty

from ehrql import case, create_dataset, maximum_of, when, years
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator
from ehrql.exceptions import CannotGenerate
from ehrql.query_language import (
    EventFrame,
    PatientFrame,
    Series,
    compile,
    table,
    table_from_rows,
)
from ehrql.tables.core import clinical_events, medications, patients


index_date = date(2022, 3, 1)

is_female_or_male = patients.sex.is_in(["female", "male"])

was_adult = (patients.age_on(index_date) >= 18) & (patients.age_on(index_date) <= 110)

was_alive = (
    patients.date_of_death.is_after(index_date) | patients.date_of_death.is_null()
)

died_more_than_10_years_ago = (patients.date_of_death + years(10)) < index_date


@table
class extra_patients(PatientFrame):
    some_integer = Series(int)


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
@pytest.mark.parametrize(
    "query",
    [
        patients.sex == "male",
        patients.date_of_birth.year == 1950,
        (patients.date_of_birth.year == 1970) & (patients.sex == "intersex"),
        ((patients.date_of_birth.year == 1970) & (patients.sex == "male"))
        | ((patients.date_of_birth.year == 1963) & (patients.sex == "male")),
        is_female_or_male & was_adult & was_alive,
        died_more_than_10_years_ago,
        patients.date_of_death.is_null(),
        ~patients.date_of_death.is_null(),
        case(
            when(patients.sex == "male").then(1),
            when(patients.sex == "female").then(2),
        )
        >= 2,
        maximum_of(patients.date_of_birth, patients.date_of_birth) <= index_date,
    ],
    ids=pretty,
)
def test_queries_with_exact_one_shot_generation(patched_time, query):
    dataset = create_dataset()

    dataset.define_population(patients.exists_for_patient() & query)

    target_size = 1000

    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    # Configure `time.time()` so we timeout after one loop pass, as we
    # should be able to generate these correctly in the first pass.
    patched_time.time.side_effect = [0.0, 20.0]
    patient_ids = {row.patient_id for row in generator.get_results()}

    assert len(patient_ids) == target_size


@st.composite
def birthday_range_query(draw):
    # We generate a single date that we require to be valid for
    # our query as a way of ensuring that the query always has
    # results.

    reasonable_dates = st.dates(min_value=date(1900, 1, 1), max_value=date(2024, 9, 1))
    valid_date = draw(reasonable_dates).replace(day=1)

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
                op = operator.le
            else:
                op = operator.lt
        else:
            if allow_equal:
                op = operator.ge
            else:
                op = operator.gt
        assert op(valid_date, endpoint)
        query_components.append(op(patients.date_of_birth, endpoint))
    while len(query_components) > 1:
        q = query_components.pop()
        i = draw(st.integers(0, len(query_components) - 1))
        query_components[i] &= q
    return query_components[0]


@example(
    query=(patients.date_of_birth >= date(2000, 1, 1))
    & (patients.date_of_birth < date(2000, 1, 2)),
    target_size=1,
)
@example(query=patients.date_of_birth < date(1900, 12, 31), target_size=1000)
@example(query=patients.date_of_birth >= date(1900, 1, 2), target_size=1000)
@example(query=patients.date_of_birth >= date(2000, 12, 1), target_size=1000)
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


@table_from_rows([(i, i, False) for i in range(1, 1000)])
class p(PatientFrame):
    i = Series(int)
    b = Series(bool)


@table
class p0(PatientFrame):
    i1 = Series(int)
    b1 = Series(bool)
    d1 = Series(date)


@table
class e0(EventFrame):
    b0 = Series(bool)
    i1 = Series(int)


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
@pytest.mark.parametrize(
    "query",
    [
        date(2010, 1, 1) < medications.date.minimum_for_patient(),
        medications.sort_by(medications.date).first_for_patient().date
        < date(2020, 1, 1),
        clinical_events.where(
            clinical_events.snomedct_code == "123456789"
        ).exists_for_patient(),
        maximum_of(patients.date_of_birth, patients.date_of_death)
        <= index_date - years(10),
        case(
            when(patients.sex == "male").then(1),
            when(patients.date_of_birth == index_date).then(2),
            otherwise=3,
        )
        >= 2,
        case(
            when(patients.date_of_birth <= index_date).then(patients.date_of_death),
            otherwise=patients.date_of_birth,
        )
        <= index_date,
        p0.i1
        < case(
            when(e0.sort_by(e0.i1).first_for_patient().b0).then(
                e0.sort_by(e0.i1).first_for_patient().i1
            ),
            otherwise=None,
        ),
        patients.date_of_birth < case(when(p0.b1).then(None), otherwise=p0.d1),
        case(when(p0.b1).then(None), otherwise=p0.d1)
        < patients.date_of_birth + years(1),
        case(when(p0.b1).then(date(2010, 1, 2)), otherwise=date(2010, 1, 1))
        > date(2010, 1, 1),
    ],
    ids=pretty,
)
def test_queries_not_yet_well_handled(patched_time, query):
    """Tests queries that we need to work, but do not currently
    expect to be handled particularly well.
    """
    dataset = create_dataset()

    dataset.define_population(patients.exists_for_patient() & query)

    target_size = 1000
    variable_definitions = compile(dataset)

    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    patched_time.time.side_effect = [0.0, 20.0]

    patient_ids = {row.patient_id for row in generator.get_results()}

    # Should be able to generate at least one patient satisfying this
    assert len(patient_ids) > 0

    # If one of these queries manages to generate fully in a single pass then
    # it deserves a more specific test. This is effectively a sort of xfail
    # assertion.
    assert len(patient_ids) < target_size


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_inline_table_query(patched_time):
    """Tests queries that we need to work, but do not currently
    expect to be handled particularly well.
    """
    dataset = create_dataset()

    dataset.define_population(p.i < 1000)
    dataset.i = p.i

    target_size = 1000
    variable_definitions = compile(dataset)

    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = target_size
    generator.timeout = 10

    patched_time.time.side_effect = [0.0, 20.0]

    patient_ids = {row.patient_id for row in generator.get_results()}

    # Should be able to generate at least one patient satisfying this
    assert len(patient_ids) > 0

    # If one of these queries manages to generate fully in a single pass then
    # it deserves a more specific test. This is effectively a sort of xfail
    # assertion.
    assert len(patient_ids) < target_size


@pytest.mark.parametrize(
    "query",
    [
        patients.sex == "book",
        extra_patients.some_integer + 1 < extra_patients.some_integer,
    ],
    ids=pretty,
)
@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_will_raise_if_all_data_is_impossible(patched_time, query):
    dataset = create_dataset()

    dataset.define_population(query)
    target_size = 1000
    variable_definitions = compile(dataset)

    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.timeout = 1
    patched_time.time.side_effect = [0.0, 20.0]
    with pytest.raises(CannotGenerate):
        generator.get_results()


def test_generates_events_starting_from_birthdate():
    dataset = create_dataset()

    age = patients.age_on("2020-03-31")

    dataset.age = age
    dataset.sex = patients.sex

    events = clinical_events.sort_by(clinical_events.date).first_for_patient()
    dataset.dob = patients.date_of_birth
    dataset.event_date = events.date
    dataset.after_dob = events.date >= patients.date_of_birth
    dataset.define_population((age > 18) & (age < 80) & ~dataset.event_date.is_null())

    target_size = 1000
    dataset.configure_dummy_data(population_size=target_size)
    variable_definitions = compile(dataset)

    generator = DummyDataGenerator(variable_definitions, population_size=target_size)

    for row in generator.get_results():
        assert row.after_dob
