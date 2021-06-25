import csv
import shutil
import sys
import time
from pathlib import Path

import docker
from docker.errors import ContainerError


client = docker.from_env()


def run_cohort_extractor(study, tmpdir, db_password):
    study_dir = tmpdir.mkdir("study")
    shutil.copy(study, study_dir)

    try:
        output = client.containers.run(
            "cohort-extractor-v2:latest",
            remove=True,
            stderr=True,
            network="test_network",
            environment={"TPP_DATABASE_URL": f"mssql://SA:{db_password}@mssql/test"},
            volumes={study_dir: {"bind": "/workspace", "mode": "rw"}},
        )

        print(str(output, "utf-8"))
    except ContainerError as e:
        print(str(e.stderr, "utf-8"), file=sys.stderr)
        raise

    return study_dir / "outputs"


def start_sql_server(tables, password):
    mssql_dir = Path(__file__).parent.absolute() / "support/mssql"

    container = client.containers.run(
        "mcr.microsoft.com/mssql/server:2017-latest",
        remove=True,
        name="mssql",
        volumes={
            mssql_dir: {"bind": "/mssql", "mode": "ro"},
            tables: {"bind": "/tables.sql", "mode": "ro"},
        },
        environment={"SA_PASSWORD": password, "ACCEPT_EULA": "Y"},
        entrypoint="/mssql/entrypoint.sh",
        command="/opt/mssql/bin/sqlservr",
        detach=True,
        network="test_network",
    )
    start = time.time()
    timeout = 10
    while True:
        exit_code, output = container.exec_run(
            [
                "/opt/mssql-tools/bin/sqlcmd",
                "-b",
                "-S",
                "localhost",
                "-U",
                "SA",
                "-P",
                password,
                "-d",
                "test",
                "-i",
                "/tables.sql",
            ]
        )
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


def create_network():
    client.networks.create("test_network")


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results / "cohort.csv") as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))

        assert actual_data == expected_data


def test_extracts_data_from_sql_server(study, tmpdir):
    our_study = study("end_to_end_tests")

    db_password = "Your_password123!"
    tables = our_study.grab_tables()
    create_network()
    start_sql_server(tables, db_password)

    study = our_study.grab_study_definition()

    actual_results = run_cohort_extractor(study, tmpdir, db_password)

    expected_results = our_study.grab_expected_results()

    assert_results_equivalent(actual_results, expected_results)
