from datetime import datetime

import pytest

from ehrql.file_formats import FILE_FORMATS
from tests.lib.fixtures import (
    database_operational_error_dataset_definition,
    invalid_dataset_attribute_dataset_definition,
    invalid_dataset_query_model_error_definition,
    no_dataset_attribute_dataset_definition,
    parameterised_dataset_definition,
    trivial_dataset_definition,
)
from tests.lib.tpp_schema import AllowedPatientsWithTypeOneDissent, Patient


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_generate_dataset(study, mssql_database, extension):
    mssql_database.setup(
        Patient(Patient_ID=1, DateOfBirth=datetime(1934, 5, 5)),
        AllowedPatientsWithTypeOneDissent(Patient_ID=1),
        Patient(Patient_ID=2, DateOfBirth=datetime(1943, 5, 5)),
        AllowedPatientsWithTypeOneDissent(Patient_ID=2),
        Patient(Patient_ID=3, DateOfBirth=datetime(1999, 5, 5)),
        AllowedPatientsWithTypeOneDissent(Patient_ID=3),
    )

    study.setup_from_string(trivial_dataset_definition)
    study.generate(mssql_database, "ehrql.backends.tpp.TPPBackend", extension=extension)
    results = study.results()

    expected = [1943, 1999]
    if extension in (".csv", ".csv.gz"):
        expected = [str(v) for v in expected]

    assert len(results) == len(expected)
    assert {r["year"] for r in results} == set(expected)


def test_parameterised_dataset_definition(study, mssql_database):
    mssql_database.setup(
        Patient(Patient_ID=1, DateOfBirth=datetime(1934, 5, 5)),
        AllowedPatientsWithTypeOneDissent(Patient_ID=1),
        Patient(Patient_ID=2, DateOfBirth=datetime(1943, 5, 5)),
        AllowedPatientsWithTypeOneDissent(Patient_ID=2),
        Patient(Patient_ID=3, DateOfBirth=datetime(1999, 5, 5)),
        AllowedPatientsWithTypeOneDissent(Patient_ID=3),
    )

    study.setup_from_string(parameterised_dataset_definition)
    study.generate(
        mssql_database,
        "ehrql.backends.tpp.TPPBackend",
        user_args={"year": "1940"},
    )
    results = study.results()

    expected = ["1943", "1999"]

    assert len(results) == len(expected)
    assert {r["year"] for r in results} == set(expected)


def test_parameterised_dataset_definition_with_bad_param(study, mssql_database, capsys):
    study.setup_from_string(parameterised_dataset_definition)
    with pytest.raises(SystemExit):
        study.generate(
            mssql_database,
            "ehrql.backends.tpp.TPPBackend",
            user_args={"ear": "1940"},
        )
    assert (
        "dataset.py: error: unrecognized arguments: --ear 1940"
        in capsys.readouterr().err
    )


def test_generate_dataset_with_database_error(study, mssql_database):
    mssql_database.setup(
        Patient(Patient_ID=1, DateOfBirth=datetime(1934, 5, 5)),
        AllowedPatientsWithTypeOneDissent(Patient_ID=1),
    )

    # This dataset definition triggers an OperationalError by implementing date
    # arithmetic that results in an out of bounds date (after 9999-12-31)
    study.setup_from_string(database_operational_error_dataset_definition)
    with pytest.raises(SystemExit) as err:
        study.generate(mssql_database, "ehrql.backends.tpp.TPPBackend")
    assert err.value.code == 5


def test_dump_dataset_sql_happy_path(study, mssql_database):
    study.setup_from_string(trivial_dataset_definition)
    study.dump_dataset_sql()


def test_dump_dataset_sql_with_no_dataset_attribute(study, mssql_database, capsys):
    study.setup_from_string(no_dataset_attribute_dataset_definition)
    with pytest.raises(SystemExit):
        study.dump_dataset_sql()
    assert (
        "Did not find a variable called 'dataset' in dataset definition file"
        in capsys.readouterr().err
    )


def test_dump_dataset_sql_attribute_invalid(study, mssql_database, capsys):
    study.setup_from_string(invalid_dataset_attribute_dataset_definition)
    with pytest.raises(SystemExit):
        study.dump_dataset_sql()
    assert "'dataset' must be an instance of ehrql.Dataset" in capsys.readouterr().err


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


def test_validate_dummy_data_error_path(study, tmp_path, capsys):
    dummy_data_file = tmp_path / "dummy.csv"
    dummy_data = "patient_id,year\n1,1971\n2,foo"
    dummy_data_file.write_text(dummy_data)
    study.setup_from_string(trivial_dataset_definition)
    with pytest.raises(SystemExit):
        study.generate(
            database=None,
            backend="expectations",
            dummy_data_file=str(dummy_data_file),
        )
    captured = capsys.readouterr()
    assert "invalid literal for int" in captured.err


def test_generate_dummy_data(study):
    study.setup_from_string(trivial_dataset_definition)
    study.generate(database=None, backend="expectations", extension=".csv")
    lines = study._dataset_path.read_text().splitlines()
    assert lines[0] == "patient_id,year"
    assert len(lines) == 11  # 1 header, 10 rows


def test_generate_dummy_data_with_dummy_tables(study, tmp_path):
    tmp_path.joinpath("patients.csv").write_text(
        "patient_id,date_of_birth\n8,1985-10-20\n9,1995-05-10"
    )
    study.setup_from_string(trivial_dataset_definition)
    study.generate(
        database=None,
        backend="expectations",
        extension=".csv",
        dummy_tables=str(tmp_path),
    )
    assert study.results() == [
        {"patient_id": "8", "year": "1985"},
        {"patient_id": "9", "year": "1995"},
    ]


def test_create_dummy_tables(study, tmp_path):
    dummy_tables_path = tmp_path / "subdir" / "dummy_data"
    study.setup_from_string(trivial_dataset_definition)
    study.create_dummy_tables(dummy_tables_path)
    lines = (dummy_tables_path / "patients.csv").read_text().splitlines()
    assert lines[0] == "patient_id,date_of_birth"
    assert len(lines) == 11  # 1 header, 10 rows
