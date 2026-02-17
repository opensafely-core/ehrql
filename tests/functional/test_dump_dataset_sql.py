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
        "Did not find a variable called 'dataset' in dataset definition file"
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
