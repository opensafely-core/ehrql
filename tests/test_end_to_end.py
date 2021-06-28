import csv
import shutil
import time
from collections import namedtuple
from pathlib import Path

import pytest
from docker.errors import ContainerError


DbDetails = namedtuple("DbDetails", ["address", "password"])


@pytest.fixture
def database(run_container):
    mssql_dir = Path(__file__).parent.absolute() / "support/mssql"
    details = DbDetails("mssql", "Your_password123!")

    run_container(
        name=details.address,
        image="mcr.microsoft.com/mssql/server:2017-latest",
        volumes={
            mssql_dir: {"bind": "/mssql", "mode": "ro"},
        },
        environment={"SA_PASSWORD": details.password, "ACCEPT_EULA": "Y"},
        entrypoint="/mssql/entrypoint.sh",
        command="/opt/mssql/bin/sqlservr",
    )

    yield details


def load_data(containers, database, tables_file, tmpdir):
    sql_dir = tmpdir.mkdir("sql")
    shutil.copy(tables_file, sql_dir)
    container_path = Path("/sql") / Path(tables_file).name
    command = [
        "/opt/mssql-tools/bin/sqlcmd",
        "-b",
        "-S",
        database.address,
        "-U",
        "SA",
        "-P",
        database.password,
        "-d",
        "test",
        "-i",
        str(container_path),
    ]

    start = time.time()
    timeout = 10
    while True:
        try:
            containers.run_fg(
                image="mcr.microsoft.com/mssql/server:2017-latest",
                volumes={
                    sql_dir: {"bind": "/sql", "mode": "ro"},
                },
                command=command,
            )
            break
        except ContainerError as e:
            if (
                b"Server is not found or not accessible" in e.stderr
                or b"Login failed for user" in e.stderr
            ) and time.time() - start < timeout:
                time.sleep(1)
            else:
                raise


def run_cohort_extractor(study, tmpdir, database, containers):
    study_dir = tmpdir.mkdir("study")
    shutil.copy(study, study_dir)

    containers.run_fg(
        image="cohort-extractor-v2:latest",
        environment={
            "TPP_DATABASE_URL": f"mssql://SA:{database.password}@{database.address}/test"
        },
        volumes={study_dir: {"bind": "/workspace", "mode": "rw"}},
    )

    return study_dir / "outputs"


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results / "cohort.csv") as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))

        assert actual_data == expected_data


def test_extracts_data_from_sql_server(study, tmpdir, database, containers):
    our_study = study("end_to_end_tests")
    load_data(containers, database, our_study.grab_tables(), tmpdir)
    actual_results = run_cohort_extractor(
        our_study.grab_study_definition(), tmpdir, database, containers
    )
    expected_results = our_study.grab_expected_results()
    assert_results_equivalent(actual_results, expected_results)
