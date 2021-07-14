import random
import sys
import time
from pathlib import Path

import docker
import docker.errors
import pytest
import sqlalchemy
import sqlalchemy.exc
from docker.errors import ContainerError
from lib import mock_backend, playback
from lib.util import get_mode
from sqlalchemy.orm import sessionmaker

import cohortextractor.main


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


def null_database():
    return DbDetails(None, None, None, None, None, None, None)


@pytest.fixture
def mssql_dir():
    return Path(__file__).parent.absolute() / "support/mssql"


def is_smoke_test(request):
    return request.node.get_closest_marker("smoke")


def is_integration_test(request):
    return request.node.get_closest_marker("integration")


# This hook makes the result of a test available during fixture teardown via the boolean `request.node.passed`.
# noinspection PyUnusedLocal
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        setattr(item, "passed", rep.passed)


@pytest.fixture
def database(request, run_container, containers, network, docker_client, mssql_dir):
    assert is_smoke_test(request) or is_integration_test(
        request
    ), "Only smoke and integration tests can use the database"
    assert not (
        is_smoke_test(request) and is_integration_test(request)
    ), "A test cannot be both a smoke test and an integration test"

    if is_smoke_test(request):
        database = make_database(
            containers, docker_client, mssql_dir, network, run_container
        )
        wait_for_database(database)
        yield database
        return

    def is_passing():
        try:
            return request.node.passed
        except AttributeError:
            return False

    with playback.recording_for(test_identifier(request), is_passing) as recording:
        database = None
        if playback.recording_mode() == "playback":
            database = DbDetails("", "", 0, "", 0, "", "")
        if playback.recording_mode() == "record":
            database = make_database(
                containers, docker_client, mssql_dir, network, run_container
            )
            with recording.suspended():
                # The queries we issue while waiting for the database will differ, so don't record them. We don't
                # wait during playback.
                wait_for_database(database)
        yield database


def test_identifier(request):
    test_module = request.module.__name__
    test_name = request.node.name
    identifier = f"{test_module}::{test_name}"
    return identifier


def make_database(containers, docker_client, mssql_dir, network, run_container):
    password = "Your_password123!"

    if database_mode() == "persistent":
        return persistent_database(containers, password, docker_client, mssql_dir)
    if database_mode() == "ephemeral":
        return ephemeral_database(run_container, password, mssql_dir, network)


def wait_for_database(database):
    url = sqlalchemy.engine.make_url(database.host_url())
    url = url.set(drivername="mssql+pymssql")
    engine = sqlalchemy.create_engine(url, future=True)

    start = time.time()
    timeout = 10
    limit = start + timeout
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(sqlalchemy.text("SELECT 'hello'"))
            break
        except sqlalchemy.exc.OperationalError as e:
            if time.time() >= limit:
                raise Exception(
                    f"Failed to connect to mssql after {timeout} seconds"
                ) from e
            time.sleep(1)


def database_mode():
    return get_mode("DATABASE", ["persistent", "ephemeral"], "persistent")


PERSISTENT_DATABASE_PORT = 49152


def persistent_database(containers, password, docker_client, mssql_dir):
    container = "cohort-extractor-mssql"
    network = "cohort-extractor-network"
    published_port = PERSISTENT_DATABASE_PORT

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
    published_port = random.randint(PERSISTENT_DATABASE_PORT + 1, 65535)

    run_container(
        name=container,
        image="mcr.microsoft.com/mssql/server:2017-CU25-ubuntu-16.04",
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


@pytest.fixture
def load_data(database):
    url = sqlalchemy.engine.make_url(database.host_url())
    url = url.set(drivername="mssql+pymssql")
    engine = sqlalchemy.create_engine(url, future=True)

    def load(file=None, sql=None):
        if file and sql:
            raise ValueError(
                "You must provide exactly one of the file or sql arguments"
            )
        if (not file) and (not sql):
            raise ValueError(
                "You must provide exactly one of the file or sql arguments"
            )

        if not sql:
            with open(file, "r") as f:
                sql = f.read()

        with engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql))

    yield load


@pytest.fixture
def setup_test_database(database):
    db_url = database.host_url()

    def setup(input_data, drivername="mssql+pymssql", base=mock_backend.Base):
        # Create engine
        url = sqlalchemy.engine.make_url(db_url)
        url = url.set(drivername=drivername)
        engine = sqlalchemy.create_engine(url, echo=True, future=True)
        # Reset the schema
        base.metadata.drop_all(engine)
        base.metadata.create_all(engine)
        # Create session
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        # Load test data
        for entity in input_data:
            session.add(entity)
            session.commit()

    return setup


def extract(cohort, backend, database):
    return list(cohortextractor.main.extract(cohort, backend(database.host_url())))
