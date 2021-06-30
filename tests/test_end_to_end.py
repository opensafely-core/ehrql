import csv
import os
import shutil
import time
from collections import namedtuple
from pathlib import Path

import docker.errors
import pytest
from docker.errors import ContainerError


DEFULT_MSSQL_PORT = 1433

DbDetails = namedtuple(
    "DbDetails",
    [
        "network",
        "host_from_container",
        "port_from_container",
        "host_from_host",
        "port_from_host",
        "password",
    ],
)


def is_fast_mode():
    return not os.environ.get("MODE") == "slow"


@pytest.fixture
def mssql_dir():
    return Path(__file__).parent.absolute() / "support/mssql"


@pytest.fixture
def database(run_container, containers, network, docker_client, mssql_dir):
    password = "Your_password123!"
    if is_fast_mode():
        yield persistent_database(containers, password, docker_client, mssql_dir)
    else:
        yield ephemeral_database(run_container, password, mssql_dir, network)


def persistent_database(containers, password, docker_client, mssql_dir):
    container = "cohort-extractor-mssql"
    network = "cohort-extractor-network"
    published_port = 12345

    try:
        docker_client.networks.get(network)
    except docker.errors.NotFound:
        docker_client.networks.create(network)

    if not containers.is_running(container):
        containers.run_bg(
            name=container,
            image="mcr.microsoft.com/mssql/server:2017-latest",
            volumes={
                mssql_dir: {"bind": "/mssql", "mode": "ro"},
            },
            network=network,
            ports={f"{DEFULT_MSSQL_PORT}/TCP": published_port},
            environment={"SA_PASSWORD": password, "ACCEPT_EULA": "Y"},
            entrypoint="/mssql/entrypoint.sh",
            command="/opt/mssql/bin/sqlservr",
        )

    return DbDetails(
        network=network,
        host_from_container=container,
        port_from_container=DEFULT_MSSQL_PORT,
        host_from_host="localhost",
        port_from_host=published_port,
        password=password,
    )


def ephemeral_database(run_container, password, mssql_dir, network):
    container = "mssql"

    run_container(
        name=container,
        image="mcr.microsoft.com/mssql/server:2017-latest",
        volumes={
            mssql_dir: {"bind": "/mssql", "mode": "ro"},
        },
        network=network,
        environment={"SA_PASSWORD": password, "ACCEPT_EULA": "Y"},
        entrypoint="/mssql/entrypoint.sh",
        command="/opt/mssql/bin/sqlservr",
    )

    return DbDetails(
        network=network,
        host_from_container=container,
        port_from_container=DEFULT_MSSQL_PORT,
        host_from_host=None,
        port_from_host=None,
        password=password,
    )


@pytest.fixture
def load_data(containers, database, tmpdir, mssql_dir):
    def load(tables_file):
        sql_dir = tmpdir.mkdir("sql")
        shutil.copy(tables_file, sql_dir)
        container_path = Path("/sql") / Path(tables_file).name
        command = [
            "/opt/mssql-tools/bin/sqlcmd",
            "-b",
            "-S",
            f"{database.host_from_container},{database.port_from_container}",
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
                        mssql_dir: {"bind": "/mssql", "mode": "ro"},
                    },
                    network=database.network,
                    entrypoint="/mssql/entrypoint.sh",
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

    return load


def container_cohort_extractor(study, database, containers, study_dir):
    shutil.copy(study, study_dir)

    containers.run_fg(
        image="cohort-extractor-v2:latest",
        environment={
            "TPP_DATABASE_URL": f"mssql://SA:{database.password}@{database.host_from_container}:{database.port_from_container}/test"
        },
        volumes={study_dir: {"bind": "/workspace", "mode": "rw"}},
        network=database.network,
    )

    return study_dir / "outputs"


def in_process_cohort_extractor(study, database, study_dir):
    shutil.copy(study, study_dir)
    from cohortextractor.main import main

    main(
        workspace=str(study_dir),
        db_url=f"mssql://SA:{database.password}@{database.host_from_host}:{database.port_from_host}/test",
    )
    return study_dir / "outputs"


@pytest.fixture
def run_cohort_extractor(tmpdir, database, containers):
    study_dir = tmpdir.mkdir("study")
    if is_fast_mode():
        return lambda study: in_process_cohort_extractor(study, database, study_dir)
    else:
        return lambda study: container_cohort_extractor(
            study, database, containers, study_dir
        )


def assert_results_equivalent(actual_results, expected_results):
    with open(actual_results / "cohort.csv") as actual_file:
        with open(expected_results) as expected_file:
            actual_data = list(csv.DictReader(actual_file))
            expected_data = list(csv.DictReader(expected_file))

        assert actual_data == expected_data


def test_extracts_data_from_sql_server(load_study, load_data, run_cohort_extractor):
    study = load_study("end_to_end_tests")
    load_data(study.tables())

    actual_results = run_cohort_extractor(study.study_definition())
    assert_results_equivalent(actual_results, study.expected_results())
