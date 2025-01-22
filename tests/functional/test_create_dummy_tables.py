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


@pytest.mark.parametrize(
    "dataset_definition_fixture,expected_columns",
    (
        # this dataset definition includes date_of_death
        # in the additional population constraints only
        (trivial_dataset_definition, "patient_id,date_of_birth,date_of_death"),
        (trivial_dataset_definition_legacy_dummy_data, "patient_id,date_of_birth"),
    ),
)
def test_create_dummy_tables(
    call_cli, tmp_path, dataset_definition_fixture, expected_columns
):
    dummy_tables_path = tmp_path / "subdir" / "dummy_data"
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition_fixture)
    call_cli("create-dummy-tables", dataset_definition_path, dummy_tables_path)
    lines = (dummy_tables_path / "patients.csv").read_text().splitlines()
    assert lines[0] == expected_columns
    assert len(lines) == 11  # 1 header, 10 rows


def test_create_dummy_tables_console_output(call_cli, tmp_path):
    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(trivial_dataset_definition)
    captured = call_cli("create-dummy-tables", dataset_definition_path)

    assert "patient_id" in captured.out
    assert "date_of_birth" in captured.out
