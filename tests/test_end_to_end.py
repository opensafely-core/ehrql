import csv
import shutil
import time
from collections import namedtuple
from pathlib import Path

import pytest


DbDetails = namedtuple("DbDetails", ["address", "password", "sql_dir", "container"])


@pytest.fixture
def database(containers, tmpdir):
    address = "mssql"
    password = "Your_password123!"
    mssql_dir = Path(__file__).parent.absolute() / "support/mssql"
    sql_dir = tmpdir.mkdir("sql")

    container = containers.run_bg(
        name=address,
        image="mcr.microsoft.com/mssql/server:2017-latest",
        volumes={
            mssql_dir: {"bind": "/mssql", "mode": "ro"},
            sql_dir: {"bind": "/sql", "mode": "ro"},
        },
        environment={"SA_PASSWORD": password, "ACCEPT_EULA": "Y"},
        entrypoint="/mssql/entrypoint.sh",
        command="/opt/mssql/bin/sqlservr",
    )

    yield DbDetails(address, password, sql_dir, container)
    containers.destroy(container)


def load_data(containers, database, tables_file):
    shutil.copy(tables_file, database.sql_dir)
    container_path = Path("/sql") / Path(tables_file).name
    command = [
        "/opt/mssql-tools/bin/sqlcmd",
        "-b",
        "-S",
        "localhost",
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
        exit_code, output = containers.exec_run(database.container, command)
        if exit_code == 0:
            break
        else:
            if (
                b"Server is not found or not accessible" in output
                or b"Login failed for user" in output
            ) and time.time() - start < timeout:
                time.sleep(1)
            else:
                raise ValueError(f"Docker error:\n{output}")


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
    load_data(containers, database, our_study.grab_tables())
    actual_results = run_cohort_extractor(
        our_study.grab_study_definition(), tmpdir, database, containers
    )
    expected_results = our_study.grab_expected_results()
    assert_results_equivalent(actual_results, expected_results)
