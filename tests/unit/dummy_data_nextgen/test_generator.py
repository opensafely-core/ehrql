import datetime
import re
from unittest import mock

import pytest

from ehrql import Dataset, create_dataset
from ehrql.dummy_data_nextgen.generator import (
    DummyDataGenerator,
    DummyPatientGenerator,
    reorder_dates,
)
from ehrql.dummy_data_nextgen.query_info import ColumnInfo, TableInfo
from ehrql.query_language import table_from_rows
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
        str,
        constraints=[
            Constraint.Categorical(["male", "female", "intersex"]),
            Constraint.NotNull(),
        ],
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
    target_size = 7

    variable_definitions = dataset._compile()
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = 4
    results = list(generator.get_results())

    # Check they look right

    assert any(r.code is not None for r in results)
    assert any(r.date is not None for r in results)

    for r in results:
        assert isinstance(r.date_of_birth, datetime.date)
        assert r.date_of_birth.day == 1
        assert r.date_of_death is None or r.date_of_death > r.date_of_birth
        assert r.sex in {"male", "female", "intersex", None}
        # To get full coverage here we need to generate enough data so that we get at
        # least one patient with a matching event and one without
        if r.code is not None or r.date is not None:
            assert r.code in {"abc", "def"}
            assert isinstance(r.date, datetime.date)
        assert r.imd in {0, 1000, 2000, 3000, 4000, 5000, None}

    assert len(results) == target_size


def test_dummy_data_generator_date_of_death_in_population_query():
    # Define a basic dataset with nullable date of death in the population query
    # This generates date of death using get_random_choice; test that None
    # values are more likely to be produced than not-None
    dataset = Dataset()
    dataset.define_population(
        patients.exists_for_patient()
        & (
            patients.date_of_death.is_after("2020-01-01")
            | patients.date_of_death.is_null()
        )
    )
    dataset.date_of_death = patients.date_of_death

    # Generate some results
    target_size = 10

    variable_definitions = dataset._compile()
    generator = DummyDataGenerator(variable_definitions, population_size=target_size)
    generator.batch_size = 7
    results = list(generator.get_results())

    assert len(results) == target_size
    date_of_death_results = [r.date_of_death for r in results]

    # Dates of death are None 70-90% of time
    assert 0.70 <= (date_of_death_results.count(None) / target_size) <= 0.9


def test_dummy_data_generator_produces_stable_results():
    # Define a basic dataset

    values = []
    for _ in range(2):
        dataset = Dataset()
        dataset.define_population(practice_registrations.exists_for_patient())
        dataset.date_of_birth = patients.date_of_birth
        dataset.date_of_death = patients.date_of_death
        dataset.sex = patients.sex
        dataset.imd = (
            addresses.sort_by(addresses.start_date).last_for_patient().imd_rounded
        )

        last_event = (
            events.where(events.code.is_in(["abc", "def"]))
            .sort_by(events.date)
            .last_for_patient()
        )
        dataset.code = last_event.code
        dataset.date = last_event.date

        generator = DummyDataGenerator.from_dataset(dataset)
        values.append(list(generator.get_results()))

    first, second = values
    assert first == second


@mock.patch("ehrql.dummy_data_nextgen.generator.time")
def test_dummy_data_generator_timeout_with_some_results(patched_time):
    dataset = Dataset()
    dataset.define_population(patients.exists_for_patient())

    variable_definitions = dataset._compile()
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
    dataset.define_population(
        (patients.date_of_birth == patients.date_of_death)
        & (patients.date_of_death.day == 2)
    )

    variable_definitions = dataset._compile()
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
    variable_definitions = dataset._compile()
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
                minimum=datetime.date(2020, 12, 5),
                maximum=datetime.date(2021, 1, 30),
            ),
            Constraint.NotNull(),
        ),
    )
    with dummy_patient_generator.seed(""):
        values = [
            dummy_patient_generator.get_random_value(column_info) for _ in range(10)
        ]
    # All generated dates should be forced to 2021-01-01
    assert len(set(values)) == 1
    assert all(value == datetime.date(2021, 1, 1) for value in values)


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


def test_get_rows_for_patients_with_first_of_month_constraint(dummy_patient_generator):
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
        rows.extend(dummy_patient_generator.get_rows(patient_id, table_info))
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
    assert all(value in [0, 2, 4, 6, 8, 10, None] for value in values), values


def test_cannot_generate_data_outside_of_a_seed_block(dummy_patient_generator):
    with pytest.raises(AssertionError):
        column_info = ColumnInfo(
            name="test",
            type=int,
            constraints=(Constraint.ClosedRange(0, 10, 2),),
        )
        dummy_patient_generator.get_random_value(column_info)


def test_get_possible_values_always_includes_none():
    column_info = ColumnInfo(
        name="test",
        type=int,
    )
    dataset = create_dataset()
    dataset.define_population(patients.exists_for_patient())
    variable_definitions = dataset._compile()

    values1 = set()
    for i in range(10):
        # Create a new generator with a different seed each time
        generator = DummyPatientGenerator(
            variable_definitions,
            random_seed=str(i),
            today=datetime.date(2024, 1, 1),
            population_size=1000,
        )
        generator.generate_patient_facts(patient_id=1)

        with generator.seed(""):
            # A random column value for a patient is chosen from the possible
            # values defined in the PopulationSubset for that patient,
            # which is a random sampling from all possible values for
            # that column
            subset = generator.get_patient_population_subset(1)
            subset_possible_values = subset.get_possible_values(column_info)
            all_possible_values = generator.get_possible_values(column_info)
            assert len(all_possible_values) > len(subset_possible_values)
            # This column allows null values, so the first item in
            # both lists is always None
            assert all_possible_values[0] is subset_possible_values[0] is None
            values1.add(subset_possible_values[1])
    # assert that we did produce more than one different subset of possible values
    assert len(values1) > 1


def test_populate_rows_with_chronological_date_columns(dummy_patient_generator):
    table_info = TableInfo(
        name="sequential_events",
        has_one_row_per_patient=False,
        columns={
            "date": ColumnInfo("date", datetime.date),
            "another_date": ColumnInfo(
                "another_date", datetime.date, constraints=(Constraint.NotNull(),)
            ),
        },
        chronological_date_columns=("date", "another_date"),
    )
    dummy_patient_generator.generate_patient_facts(1)
    rows = [{} for _ in range(10)]
    with dummy_patient_generator.seed(""):
        for i, row in enumerate(rows):
            dummy_patient_generator.populate_row(i + 1, table_info, row)
    assert all(
        row["date"] is None or row["another_date"] >= row["date"] for row in rows
    )
    assert any(row["date"] is not None for row in rows)


def test_reorder_dates():
    row = {
        "date_1": datetime.date(2000, 1, 1),
        "date_2": datetime.date(2020, 1, 1),
        "date_3": datetime.date(2010, 1, 1),
    }
    reorder_dates(row, ["date_1", "date_2", "date_3"])
    assert row == {
        "date_1": datetime.date(2000, 1, 1),
        "date_2": datetime.date(2010, 1, 1),
        "date_3": datetime.date(2020, 1, 1),
    }


def test_reorder_dates_ignores_other_columns():
    row = {
        "date_1": datetime.date(2020, 1, 1),
        "date_2": datetime.date(2000, 1, 1),
        "date_3": datetime.date(2010, 1, 1),
    }
    reorder_dates(row, ["date_1", "date_2"])
    assert row == {
        "date_1": datetime.date(2000, 1, 1),
        "date_2": datetime.date(2020, 1, 1),
        "date_3": datetime.date(2010, 1, 1),
    }


def test_reorder_dates_ignores_nulls():
    row = {
        "date_1": None,
        "date_2": datetime.date(2010, 1, 1),
        "date_3": None,
        "date_4": datetime.date(2000, 1, 1),
    }
    reorder_dates(row, ["date_1", "date_2", "date_3", "date_4"])
    assert row == {
        "date_1": None,
        "date_2": datetime.date(2000, 1, 1),
        "date_3": None,
        "date_4": datetime.date(2010, 1, 1),
    }


def test_reorder_dates_when_all_null():
    row = {"date_1": None, "date_2": None}
    reorder_dates(row, ["date_1", "date_2"])
    assert row == {"date_1": None, "date_2": None}


def test_choose_random_value(dummy_patient_generator, monkeypatch):
    randrange_calls = []

    def mock_randrange(lo, hi):
        randrange_calls.append((lo, hi))
        return lo

    column_info = ColumnInfo(
        name="date",
        type=datetime.date,
        constraints=(),
    )
    possible_values = [datetime.date(2020, 1, d) for d in range(1, 32)]

    with dummy_patient_generator.seed(""):
        # Choose an invalid value first - otherwise we would exit early
        monkeypatch.setattr(
            dummy_patient_generator.rnd, "choice", lambda _: datetime.date(2999, 1, 1)
        )
        monkeypatch.setattr(dummy_patient_generator.rnd, "randrange", mock_randrange)

        unconstrained = dummy_patient_generator.choose_random_value(
            column_info, possible_values, None
        )

        constrained = dummy_patient_generator.choose_random_value(
            column_info,
            possible_values,
            Constraint.GeneralRange(maximum=datetime.date(2020, 1, 1)),
        )

    assert randrange_calls == [(0, 31), (0, 1)]
    assert unconstrained == datetime.date(2020, 1, 1)
    assert constrained == datetime.date(2020, 1, 1)


@pytest.fixture(scope="module")
def dummy_patient_generator():
    dataset = Dataset()
    dataset.define_population(patients.exists_for_patient())
    variable_definitions = dataset._compile()
    generator = DummyPatientGenerator(
        variable_definitions,
        random_seed="abc",
        today=datetime.date(2024, 1, 1),
        population_size=1000,
    )
    generator.generate_patient_facts(patient_id=1)
    # Ensure that this patient has a long enough history that we get a sensible
    # distribution of event dates (the fixed random seed above should ensure that the
    # history length is always the same; this check is here as a failsafe)
    assert (generator.event_range.maximum - generator.event_range.minimum).days > 365
    return generator
