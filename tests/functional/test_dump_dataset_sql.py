import pytest

from tests.lib.inspect_utils import function_body_as_string


def test_dump_dataset_sql_happy_path(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition():
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

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)

    captured = call_cli("dump-dataset-sql", dataset_definition_path)

    assert "SELECT" in captured.out


def test_dump_dataset_sql_custom_unique_id(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition():
        from ehrql import create_dataset
        from ehrql.tables.core import patients

        dataset = create_dataset()
        dataset.define_population(patients.date_of_birth.year >= 2000)

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)

    captured = call_cli(
        "dump-dataset-sql",
        dataset_definition_path,
        "--query-engine",
        "mssql",
        environ={"EHRQL_GLOBAL_UNIQUE_ID": "test_id_abc"},
    )

    assert "test_id_abc" in captured.out


def test_dump_dataset_sql_with_measures(call_cli, tmp_path):
    @function_body_as_string
    def measures_definition():
        from ehrql import INTERVAL, create_measures, months
        from ehrql.tables.core import patients

        measures = create_measures()
        measures.define_measure(
            name="deaths",
            numerator=patients.is_dead_on(INTERVAL.end_date),
            denominator=patients.is_alive_on(INTERVAL.start_date),
            group_by={"sex": patients.sex},
            intervals=months(3).starting_on("2025-01-01"),
        )

    definition_path = tmp_path / "definition.py"
    definition_path.write_text(measures_definition)

    captured = call_cli("dump-dataset-sql", definition_path)

    assert "SELECT" in captured.out


def test_dump_dataset_sql_with_no_dataset_attribute(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition():
        from ehrql import create_dataset
        from ehrql.tables.tpp import patients

        my_dataset = create_dataset()
        year = patients.date_of_birth.year
        my_dataset.define_population(year >= 1900)

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)

    with pytest.raises(SystemExit):
        call_cli("dump-dataset-sql", dataset_definition_path)
    assert (
        "Did not find a variable called 'dataset' or 'measures' in the definition file"
        in call_cli.readouterr().err
    )


def test_dump_dataset_sql_attribute_invalid(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition():
        from ehrql import create_dataset  # noqa
        from ehrql.tables.tpp import patients

        dataset = patients  # noqa

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)

    with pytest.raises(SystemExit):
        call_cli("dump-dataset-sql", dataset_definition_path)
    assert "'dataset' must be an instance of ehrql.Dataset" in call_cli.readouterr().err


def test_dump_dataset_sql_query_model_error(call_cli, tmp_path):
    @function_body_as_string
    def dataset_definition():
        from ehrql.tables.tpp import patients

        # Odd construction is required to get an error that comes from inside library code.
        patients.date_of_birth.year + (patients.sex.is_null())

    dataset_definition_path = tmp_path / "dataset_definition.py"
    dataset_definition_path.write_text(dataset_definition)

    with pytest.raises(SystemExit) as exc_info:
        call_cli("dump-dataset-sql", dataset_definition_path)

    assert exc_info.value.code > 0
    captured = call_cli.readouterr()
    assert "patients.date_of_birth.year + (patients.sex.is_null())" in captured.err
    assert "main.py" not in captured.err
