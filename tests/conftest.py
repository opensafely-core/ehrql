import os
import shutil
import sys
import time
from pathlib import Path

import docker
import docker.errors
import pytest
from docker.errors import ContainerError


class Study:
    def __init__(self, study_path):
        super().__init__()
        self._path = Path(__file__).parent.absolute() / "fixtures" / study_path

    def tables(self):
        return self._path / "tables.sql"

    def study_definition(self):
        return self._path / "study_definition.py"

    def expected_results(self):
        return self._path / "results.csv"


@pytest.fixture
def load_study():
    def read_dir(path):
        return Study(path)

    return read_dir


@pytest.fixture
def docker_client():
    yield docker.from_env()


@pytest.fixture
def network(docker_client):
    name = "test_network"
    docker_client.networks.create(name)
    yield name
    docker_client.networks.get(name).remove()


class Containers:
    def __init__(self, docker_client):
        self._docker = docker_client

    def is_running(self, name):
        try:
            container = self._docker.containers.get(name)
            return container.status == "running"
        except docker.errors.NotFound:
            return False

    # All available arguments documented here:
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    def run_bg(self, name, image, **kwargs):
        return self._run(name=name, image=image, detach=True, **kwargs)

    # All available arguments documented here:
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    def run_fg(self, image, **kwargs):
        try:
            output = self._run(image=image, detach=False, stderr=True, **kwargs)
            print(str(output, "utf-8"))
        except ContainerError as e:
            print(str(e.stderr, "utf-8"), file=sys.stderr)
            raise

    # noinspection PyMethodMayBeStatic
    def destroy(self, container):
        container.remove(force=True)

    def _run(self, **kwargs):
        return self._docker.containers.run(remove=True, **kwargs)


@pytest.fixture
def containers(docker_client, network):
    # `network` is specified as an argument for sequencing reasons. We need to make sure that the network is created
    # before containers that use it and that all containers are cleaned up before the network is removed.
    yield Containers(docker_client)


@pytest.fixture
def run_container(containers):
    container = None

    def run(**kwargs):
        nonlocal container
        container = containers.run_bg(**kwargs)

    yield run
    if container:
        # noinspection PyTypeChecker
        containers.destroy(container)


DEFAULT_MSSQL_PORT = 1433


class DbDetails:
    def __init__(
        self,
        network,
        host_from_container,
        port_from_container,
        host_from_host,
        port_from_host,
        password,
        db_name,
    ):
        self.network = network
        self.host_from_container = host_from_container
        self.port_from_container = port_from_container
        self.host_from_host = host_from_host
        self.port_from_host = port_from_host
        self.password = password
        self.db_name = db_name

    def host_url(self):
        return self._url(self.host_from_host, self.port_from_host)

    def container_url(self):
        return self._url(self.host_from_container, self.port_from_container)

    def _url(self, host, port):
        return f"mssql://SA:{self.password}@{host}:{port}/{self.db_name}"


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
            ports={f"{DEFAULT_MSSQL_PORT}/TCP": published_port},
            environment={"SA_PASSWORD": password, "ACCEPT_EULA": "Y"},
            entrypoint="/mssql/entrypoint.sh",
            command="/opt/mssql/bin/sqlservr",
        )

    return DbDetails(
        network=network,
        host_from_container=container,
        port_from_container=DEFAULT_MSSQL_PORT,
        host_from_host="localhost",
        port_from_host=published_port,
        password=password,
        db_name="test",
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
        port_from_container=DEFAULT_MSSQL_PORT,
        host_from_host=None,
        port_from_host=None,
        password=password,
        db_name="test",
    )


@pytest.fixture
def load_data(containers, database, tmpdir, mssql_dir):
    filename = "data.sql"
    host_dir = tmpdir.mkdir("sql")
    host_file = host_dir / filename
    container_dir = Path("/sql")
    container_file = container_dir / filename

    def load(file=None, sql=None):
        if file and sql:
            raise ValueError(
                "You must provide exactly one of the file or sql arguments"
            )
        elif file:
            shutil.copy(file, host_file)
        elif sql:
            host_file.write(sql)
        else:
            raise ValueError(
                "You must provide exactly one of the file or sql arguments"
            )

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
            str(container_file),
        ]

        start = time.time()
        timeout = 10
        while True:
            try:
                containers.run_fg(
                    image="mcr.microsoft.com/mssql/server:2017-latest",
                    volumes={
                        host_dir: {"bind": str(container_dir), "mode": "ro"},
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
