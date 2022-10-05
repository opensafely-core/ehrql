from datetime import datetime

import pytest

from databuilder.file_formats import FILE_FORMATS, ValidationError
from tests.lib.fixtures import (
    invalid_dataset_attribute_dataset_definition,
    invalid_dataset_query_model_error_definition,
    no_dataset_attribute_dataset_definition,
    trivial_dataset_definition,
)
from tests.lib.tpp_schema import patient


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_generate_dataset(study, mssql_database, extension):
    mssql_database.setup(
        patient(dob=datetime(1943, 5, 5)),
        patient(dob=datetime(1999, 5, 5)),
    )

    study.setup_from_string(trivial_dataset_definition)
    study.generate(
        mssql_database, "databuilder.backends.tpp.TPPBackend", extension=extension
    )
    results = study.results()

    expected = [1943, 1999]
    if extension in (".csv", ".csv.gz"):
        expected = [str(v) for v in expected]

    assert len(results) == len(expected)
    assert {r["year"] for r in results} == set(expected)


def test_dump_dataset_sql_happy_path(study, mssql_database):
    study.setup_from_string(trivial_dataset_definition)
    study.dump_dataset_sql()


def test_dump_dataset_sql_with_no_dataset_attribute(study, mssql_database):
    study.setup_from_string(no_dataset_attribute_dataset_definition)
    with pytest.raises(
        AttributeError, match="A dataset definition must define one 'dataset'"
    ):
        study.dump_dataset_sql()


def test_dump_dataset_sql_attribute_invalid(study, mssql_database):
    study.setup_from_string(invalid_dataset_attribute_dataset_definition)
    with pytest.raises(
        AssertionError,
        match="'dataset' must be an instance of databuilder.ehrql.Dataset()",
    ):
        study.dump_dataset_sql()


def test_dump_dataset_sql_query_model_error(study, mssql_database, capsys):
    study.setup_from_string(invalid_dataset_query_model_error_definition)
    with pytest.raises(SystemExit) as exc_info:
        study.dump_dataset_sql()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "patients.date_of_birth.year + (patients.sex.is_null())" in captured.err
    assert "main.py" not in captured.err


def test_validate_dummy_data_happy_path(study, tmp_path):
    dummy_data_file = tmp_path / "dummy.csv"
    dummy_data = "patient_id,year\n1,1971\n2,1992"
    dummy_data_file.write_text(dummy_data)
    study.setup_from_string(trivial_dataset_definition)
    study.generate(
        database=None,
        backend="expectations",
        dummy_data_file=str(dummy_data_file),
    )
    assert study.results() == [
        {"patient_id": "1", "year": "1971"},
        {"patient_id": "2", "year": "1992"},
    ]


def test_validate_dummy_data_error_path(study, tmp_path):
    dummy_data_file = tmp_path / "dummy.csv"
    dummy_data = "patient_id,year\n1,1971\n2,foo"
    dummy_data_file.write_text(dummy_data)
    study.setup_from_string(trivial_dataset_definition)
    with pytest.raises(ValidationError, match="invalid literal for int"):
        study.generate(
            database=None,
            backend="expectations",
            dummy_data_file=str(dummy_data_file),
        )
