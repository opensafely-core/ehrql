import textwrap
from datetime import datetime

import pytest

from tests.lib import fixtures
from tests.lib.docker import ContainerError
from tests.lib.tpp_schema import Patient, RegistrationHistory


def test_generate_dataset_in_container(study, mssql_database):
    mssql_database.setup(
        Patient(
            Patient_ID=1,
            DateOfBirth=datetime(1943, 5, 5),
        ),
        RegistrationHistory(Patient_ID=1, StartDate=datetime(2000, 1, 1)),
    )

    study.setup_from_string(fixtures.trivial_dataset_definition)
    study.generate_in_docker(mssql_database, "ehrql.backends.tpp.TPPBackend")
    results = study.results()

    assert len(results) == 1
    assert results[0]["year"] == "1943"


def test_dump_dataset_sql_in_container(study):
    study.setup_from_string(fixtures.trivial_dataset_definition)
    study.dump_dataset_sql_in_docker()
    # non-zero exit raises an exception


def test_generate_dataset_with_disallowed_operations_in_container(
    study, mssql_database
):
    # End-to-end test to confirm that disallowed operations are blocked when running
    # inside the Docker container. Obviously the below is not a valid dataset definition
    # but we're interested in whether it raises a permissions error vs some other sort
    # of error.
    dataset_definition = textwrap.dedent(
        """\
        import socket

        # If code isolation is working correctly this should raise a permissions error
        # rather than a timeout
        try:
            socket.create_connection(("192.0.2.0", 53), timeout=0.001)
        except TimeoutError:
            pass
        """
    )
    study.setup_from_string(dataset_definition)
    with pytest.raises(
        ContainerError, match=r"PermissionError: \[Errno 1\] Operation not permitted"
    ):
        study.generate_in_docker(mssql_database, "tpp")


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
