import pytest

from tests.lib.file_utils import read_file_as_dicts
from tests.lib.inspect_utils import function_body_as_string


pytestmark = [pytest.mark.dummy_data, pytest.mark.dummy_data_smoke]


@function_body_as_string
def dataset_definition_population_stress():
    from ehrql import create_dataset
    from ehrql.tables.core import patients

    dataset = create_dataset()
    dataset.define_population(patients.exists_for_patient())
    dataset.year_of_birth = patients.date_of_birth.year
    dataset.age_on_2020 = patients.age_on("2020-01-01")
    dataset.sex = patients.sex
    dataset.configure_dummy_data(
        population_size=2000,
        timeout=60,
        additional_population_constraint=(
            patients.date_of_death.is_null()
            | patients.date_of_death.is_on_or_after("2020-01-01")
        ),
    )


@function_body_as_string
def dataset_definition_event_heavy():
    from ehrql import claim_permissions, create_dataset
    from ehrql.tables.core import clinical_events, patients

    claim_permissions("event_level_data")

    dataset = create_dataset()
    dataset.define_population(patients.exists_for_patient())
    dataset.birth_year = patients.date_of_birth.year
    dataset.has_death_record = patients.date_of_death.is_not_null()

    events_recent = clinical_events.where(
        clinical_events.date.is_on_or_after("2016-01-01")
        & clinical_events.date.is_on_or_before("2020-12-31")
    )
    dataset.add_event_table(
        "events_recent",
        date=events_recent.date,
        code=events_recent.snomedct_code,
        numeric_value=events_recent.numeric_value,
    )
    high_value_events = events_recent.where(
        events_recent.snomedct_code.is_in(["123456", "654321"])
    )
    dataset.add_event_table(
        "high_value_events",
        date=high_value_events.date,
        code=high_value_events.snomedct_code,
    )

    dataset.configure_dummy_data(population_size=800, timeout=60)


@function_body_as_string
def measures_definition_population_stress():
    from ehrql import Measures, years
    from ehrql.tables.core import clinical_events, patients

    measures = Measures()

    measures.configure_dummy_data(population_size=1500, timeout=60)

    events = clinical_events.where(clinical_events.date.is_on_or_after("2018-01-01"))

    measures.define_measure(
        "events_rate_by_sex",
        numerator=events.count_for_patient(),
        denominator=patients.exists_for_patient(),
        group_by={"sex": patients.sex},
        intervals=years(1).starting_on("2019-01-01"),
    )
    measures.define_measure(
        "events_with_values_by_birth_year",
        numerator=events.where(events.numeric_value.is_not_null()).count_for_patient(),
        denominator=patients.exists_for_patient(),
        group_by={"birth_year": patients.date_of_birth.year},
        intervals=years(1).starting_on("2019-01-01"),
    )


def test_dummy_data_smoke_population_stress(call_cli, tmp_path):
    dataset_file = tmp_path / "dataset_population.py"
    dataset_file.write_text(dataset_definition_population_stress)
    output_file = tmp_path / "population.csv"

    call_cli(
        "generate-dataset",
        dataset_file,
        "--output",
        output_file,
    )

    rows = read_file_as_dicts(output_file)

    assert len(rows) == 2000
    assert all(row["year_of_birth"] for row in rows)
    assert all(row["age_on_2020"] for row in rows)


def test_dummy_data_smoke_event_heavy(call_cli, tmp_path):
    dataset_file = tmp_path / "dataset_events.py"
    dataset_file.write_text(dataset_definition_event_heavy)
    output_dir = tmp_path / "events_output"

    call_cli(
        "generate-dataset",
        dataset_file,
        "--output",
        f"{output_dir}:csv",
    )

    dataset_rows = read_file_as_dicts(output_dir / "dataset.csv")
    assert len(dataset_rows) == 800

    recent_event_path = output_dir / "events_recent.csv"
    high_value_path = output_dir / "high_value_events.csv"

    assert recent_event_path.exists()
    assert high_value_path.exists()

    recent_rows = read_file_as_dicts(recent_event_path)
    high_value_rows = read_file_as_dicts(high_value_path)

    assert len(recent_rows) > 0
    assert len(high_value_rows) > 0
    assert {"patient_id", "date", "code"} <= recent_rows[0].keys()


def test_dummy_measures_smoke(call_cli, tmp_path):
    measures_file = tmp_path / "measures.py"
    measures_file.write_text(measures_definition_population_stress)
    output_file = tmp_path / "measures.csv"

    call_cli(
        "generate-measures",
        measures_file,
        "--output",
        output_file,
    )

    rows = read_file_as_dicts(output_file)
    assert len(rows) >= 8

    for row in rows:
        assert row["numerator"] != ""
        assert row["denominator"] != ""
