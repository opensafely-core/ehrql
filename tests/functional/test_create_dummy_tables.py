import pytest

from tests.lib.inspect_utils import function_body_as_string


@function_body_as_string
def trivial_dataset_definition():
    from ehrql import create_dataset
    from ehrql.tables.tpp import patients

    dataset = create_dataset()
    year = patients.date_of_birth.year
    dataset.define_population(year >= 1940)
    dataset.year = year

    dataset.configure_dummy_data(
        population_size=10,
        additional_population_constraint=patients.date_of_death.is_null(),
    )


@function_body_as_string
def trivial_dataset_definition_legacy_dummy_data():
    from ehrql import create_dataset
    from ehrql.tables.tpp import patients

    dataset = create_dataset()
    year = patients.date_of_birth.year
    dataset.define_population(year >= 1940)
    dataset.year = year

    dataset.configure_dummy_data(population_size=10, legacy=True)


@function_body_as_string
def trivial_measures_definition():
    from ehrql import INTERVAL, Measures, years
    from ehrql.tables.core import patients

    measures = Measures()

    measures.define_measure(
        "births",
        numerator=patients.date_of_birth.is_on_or_after(INTERVAL.start_date),
        denominator=patients.exists_for_patient(),
        group_by={"sex": patients.sex},
        intervals=years(2).starting_on("1940-01-01"),
    )


@pytest.mark.parametrize(
    "dataset_definition_fixture,expected_columns,expected_count",
    (
        # this dataset definition includes date_of_death
        # in the additional population constraints only
        (trivial_dataset_definition, "patient_id,date_of_birth,date_of_death", 11),
        (trivial_dataset_definition_legacy_dummy_data, "patient_id,date_of_birth", 11),
        (trivial_measures_definition, "patient_id,date_of_birth,sex", 21),
    ),
)
def test_create_dummy_tables(
    call_cli, tmp_path, dataset_definition_fixture, expected_columns, expected_count
):
    dummy_tables_path = tmp_path / "subdir" / "dummy_data"
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition_fixture)
    call_cli("create-dummy-tables", dataset_definition_path, dummy_tables_path)
    lines = (dummy_tables_path / "patients.csv").read_text().splitlines()
    assert lines[0] == expected_columns
    assert len(lines) == expected_count  # 1 header, 10 rows (x2 intervals for measures)


def test_create_dummy_tables_console_output(call_cli, tmp_path):
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(trivial_dataset_definition)
    captured = call_cli("create-dummy-tables", dataset_definition_path)

    assert "patient_id" in captured.out
    assert "date_of_birth" in captured.out
