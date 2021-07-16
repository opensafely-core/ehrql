from pathlib import Path

import docker
import docker.errors
import pytest
import sqlalchemy
import sqlalchemy.exc
from lib import mock_backend, playback
from lib.databases import DbDetails, make_database, wait_for_database
from lib.docker import Containers
from lib.tpp_schema import Base
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def docker_client():
    yield docker.from_env()


@pytest.fixture
def network(docker_client):
    name = "test_network"
    docker_client.networks.create(name)
    try:
        yield name
    finally:
        docker_client.networks.get(name).remove()


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

    try:
        yield run
    finally:
        if container:
            # noinspection PyTypeChecker
            containers.destroy(container)


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


@pytest.fixture
def setup_tpp_database(setup_test_database):
    def setup(data):
        setup_test_database(data, base=Base)

    yield setup
