import datetime
import re
from unittest import mock

import pytest

from ehrql import Dataset
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator, DummyPatientGenerator
from ehrql.dummy_data_nextgen.query_info import ColumnInfo, TableInfo
from ehrql.query_language import compile, table_from_rows
from ehrql.tables import Constraint, EventFrame, PatientFrame, Series, table


class NotNull:
    """
    Useful for pytest assertions where we don't care what a value nested in a dictionary
    is, just that it isn't null
    """

    def __eq__(self, other):
        return other is not None

    def __repr__(self):  # pragma: no cover
        return f"{self.__class__.__name__}()"


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


@table
class addresses(EventFrame):
    start_date = Series(datetime.date)
    imd_rounded = Series(int, constraints=[Constraint.ClosedRange(0, 5000, 1000)])


def test_dummy_data_generator():
    # Define a basic dataset
    dataset = Dataset()
    dataset.define_population(practice_registrations.exists_for_patient())
    dataset.date_of_birth = patients.date_of_birth
    dataset.date_of_death = patients.date_of_death
    dataset.sex = patients.sex
    dataset.imd = addresses.sort_by(addresses.start_date).last_for_patient().imd_rounded

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
        assert r.imd in {0, 1000, 2000, 3000, 4000, 5000}


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
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

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Within that table expecting "2 loops * 3 patients" worth of data
    assert len(data_for_table) == 6


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
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

    # Expecting a single table
    assert len(data) == 1
    data_for_table = list(data.values())[0]
    # Expecting no data for that table
    assert len(data_for_table) == 0


# Every combination here exercises slightly different codes paths and has different
# failure modes so we need to test them all
@pytest.mark.parametrize("population_has_inline_table_only", [True, False])
@pytest.mark.parametrize("dataset_has_inline_table_only", [True, False])
@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_dummy_data_generator_with_inline_patient_table(
    patched_time, population_has_inline_table_only, dataset_has_inline_table_only
):
    # We're deliberately using high valued IDs here which the dummy data system wouldn't
    # naturally generate
    @table_from_rows(
        [
            # Plus one low-valued ID which we _do_ expect it to generate
            (1, 1),
            (1234567890, 2),
            (1234567891, 3),
            (1234567892, 4),
            (1234567893, 5),
            (1234567894, 6),
        ]
    )
    class inline_table(PatientFrame):
        i = Series(int)

    # Define a basic dataset
    dataset = Dataset()
    dataset.i = inline_table.i

    # We don't particularly care what the variables are here, we just need to ensure we
    # include a reference a non-inline table or not, as appropriate
    if dataset_has_inline_table_only:
        dataset.j = inline_table.i + 1
    else:
        dataset.j = patients.sex

    # Likewise for the population: there's no signficance to the specific definition
    # here other than whether or not it includes a reference to a non-inline table
    if population_has_inline_table_only:
        dataset.define_population(inline_table.exists_for_patient())
    else:
        dataset.define_population(
            inline_table.exists_for_patient() & patients.date_of_birth.is_not_null()
        )

    # Generate some results
    variable_definitions = compile(dataset)
    generator = DummyDataGenerator(variable_definitions)
    # We're asking for more results than we can possibly get (because there are only 6
    # patients in the inline table). We expect the attempt to timeout and just return 6
    # results.
    generator.population_size = 10
    generator.timeout = 10
    generator.batch_size = 10
    # Configure `time.time()` so we timeout after two loop passes
    patched_time.time.side_effect = [0.0, 5.0, 20.0]

    results = [row._asdict() for row in generator.get_results()]

    assert results == [
        {"patient_id": 1, "i": 1, "j": NotNull()},
        {"patient_id": 1234567890, "i": 2, "j": NotNull()},
        {"patient_id": 1234567891, "i": 3, "j": NotNull()},
        {"patient_id": 1234567892, "i": 4, "j": NotNull()},
        {"patient_id": 1234567893, "i": 5, "j": NotNull()},
        {"patient_id": 1234567894, "i": 6, "j": NotNull()},
    ]


@pytest.mark.parametrize("type_", [bool, int, float, str, datetime.date])
def test_dummy_patient_generator_get_random_value(dummy_patient_generator, type_):
    with dummy_patient_generator.seed(""):
        column_info = ColumnInfo(name="test", type=type_)
        value = dummy_patient_generator.get_random_value(column_info)
        assert isinstance(value, type_)


def test_get_random_value_on_first_of_month(dummy_patient_generator):
    column_info = ColumnInfo(
        name="test",
        type=datetime.date,
        constraints=(Constraint.FirstOfMonth(),),
    )
    with dummy_patient_generator.seed(""):
        values = [
            dummy_patient_generator.get_random_value(column_info) for _ in range(10)
        ]
        assert len(set(values)) > 1, "dates are all identical"
        assert all(value.day == 1 for value in values)


def test_get_random_value_on_first_of_month_with_last_month_minimum(
    dummy_patient_generator,
):
    column_info = ColumnInfo(
        name="test",
        type=datetime.date,
        constraints=(
            Constraint.FirstOfMonth(),
            Constraint.GeneralRange(
                minimum=datetime.datetime(2020, 12, 5),
                maximum=datetime.datetime(2021, 1, 30),
            ),
        ),
    )
    with dummy_patient_generator.seed(""):
        values = [
            dummy_patient_generator.get_random_value(column_info) for _ in range(10)
        ]
    # All generated dates should be forced to 2021-01-01
    assert len(set(values)) == 1
    assert all(value == datetime.datetime(2021, 1, 1) for value in values)


def test_get_random_str(dummy_patient_generator):
    column_info = ColumnInfo(name="test", type=str)
    with dummy_patient_generator.seed(""):
        values = [
            dummy_patient_generator.get_random_value(column_info) for _ in range(10)
        ]
    lengths = {len(s) for s in values}
    assert len(lengths) > 1, "strings are all the same length"


def test_get_random_str_with_regex(dummy_patient_generator):
    column_info = ColumnInfo(
        name="test",
        type=str,
        constraints=(Constraint.Regex("AB[X-Z]{5}"),),
    )
    with dummy_patient_generator.seed(""):
        values = [
            dummy_patient_generator.get_random_value(column_info) for _ in range(10)
        ]
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
    for patient_id in range(10):
        dummy_patient_generator.generate_patient_facts(patient_id)
        rows.extend(dummy_patient_generator.rows_for_patients(table_info))
    assert len(rows) == 10
    # Assert constraints are respected
    assert all(r["date_of_birth"] is not None for r in rows)
    assert any(r["date_of_birth"].day != 1 for r in rows)  # pragma: no branch
    assert all(r["date_of_death"] is None or r["date_of_death"].day == 1 for r in rows)


def test_get_random_int_with_range(dummy_patient_generator):
    column_info = ColumnInfo(
        name="test",
        type=int,
        constraints=(Constraint.ClosedRange(0, 10, 2),),
    )
    with dummy_patient_generator.seed(""):
        values = [
            dummy_patient_generator.get_random_value(column_info) for _ in range(10)
        ]
    assert all(value in [0, 2, 4, 6, 8, 10] for value in values), values


def test_cannot_generate_data_outside_of_a_seed_block(dummy_patient_generator):
    with pytest.raises(AssertionError):
        column_info = ColumnInfo(
            name="test",
            type=int,
            constraints=(Constraint.ClosedRange(0, 10, 2),),
        )
        dummy_patient_generator.get_random_value(column_info)


@pytest.fixture(scope="module")
def dummy_patient_generator():
    dataset = Dataset()
    dataset.define_population(patients.exists_for_patient())
    variable_definitions = compile(dataset)
    generator = DummyPatientGenerator(
        variable_definitions,
        random_seed="abc",
        today=datetime.date(2024, 1, 1),
    )
    generator.generate_patient_facts(patient_id=1)
    # Ensure that this patient has a long enough history that we get a sensible
    # distribution of event dates (the fixed random seed above should ensure that the
    # history length is always the same; this check is here as a failsafe)
    assert (generator.events_end - generator.events_start).days > 365
    return generator
