from datetime import datetime

from tests.lib import fixtures
from tests.lib.tpp_schema import Patient


def test_generate_dataset_in_container(study, mssql_database):
    mssql_database.setup(Patient(Patient_ID=1, DateOfBirth=datetime(1943, 5, 5)))

    study.setup_from_string(fixtures.trivial_dataset_definition)
    stderr = study.generate_in_docker(mssql_database, "ehrql.backends.tpp.TPPBackend")
    results = study.results()

    assert len(results) == 1
    assert results[0]["year"] == "1943"

    assert b"Warning" not in stderr


def test_dump_dataset_sql_in_container(study):
    study.setup_from_string(fixtures.trivial_dataset_definition)
    # non-zero exit raises an exception
    stderr = study.dump_dataset_sql_in_docker()
    assert b"Warning" not in stderr


def test_generate_measures_in_container(run_in_container):
    output = run_in_container(
        [
            "generate-measures",
            "--help",
        ]
    )

    assert output


def test_test_connection_in_container(run_in_container):
    output = run_in_container(
        [
            "test-connection",
            "--help",
        ]
    )

    assert output
