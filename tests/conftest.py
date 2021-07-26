from contextlib import contextmanager
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
def docker_client(request):
    yield request.session.docker_client


@pytest.fixture
def network(request):
    yield request.session.network_name


@pytest.fixture
def containers(request):
    yield Containers(request.session.docker_client)


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
def recording(request):
    if is_smoke_test(request):
        yield DummyRecording()
        return

    def is_passing():
        try:
            return request.node.passed
        except AttributeError:
            return False

    with playback.recording_for(test_identifier(request), is_passing) as recording:
        yield recording


class DummyRecording:
    @contextmanager
    def suspended(self):
        yield


def test_identifier(request):
    test_module = request.module.__name__
    test_name = request.node.name
    identifier = f"{test_module}::{test_name}"
    return identifier


@pytest.fixture
def database(request, recording, containers, docker_client, network):
    assert is_smoke_test(request) or is_integration_test(
        request
    ), "Only smoke and integration tests can use the database"
    assert not (
        is_smoke_test(request) and is_integration_test(request)
    ), "A test cannot be both a smoke test and an integration test"

    if is_smoke_test(request) or playback.recording_mode() == "record":
        if request.session.database is None:
            container, database = make_database(
                containers, docker_client, mssql_dir(), network
            )
            wait_for_database(database)
            request.session.container = container
            request.session.database = database
        yield request.session.database
    else:
        yield request.session.playback_database


@pytest.fixture
def setup_test_database(database, recording, request):
    db_url = database.host_url()

    def setup(input_data, drivername="mssql+pymssql", base=mock_backend.Base):
        if is_integration_test(request) and playback.recording_mode() == "playback":
            # Since we suspend recording during setup, we must skip it altogether during playback.
            return

        with recording.suspended():
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
    def setup(*data):
        setup_test_database(data, base=Base)

    yield setup


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and before performing collection
    and entering the run test loop.
    Set up the session-based docker client and database.
    """
    session.docker_client = docker.from_env()
    session.network_name = "test_network"
    session.docker_client.networks.create(session.network_name)
    containers = Containers(session.docker_client)

    session.playback_database = DbDetails("", "", 0, "", 0, "", "")
    session.container = None
    session.database = None
    if playback.recording_mode() != "playback":
        session.container, session.database = make_database(
            containers, session.docker_client, mssql_dir(), session.network_name
        )
        wait_for_database(session.database)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    containers = Containers(session.docker_client)
    if session.container:
        containers.destroy(containers.get_container(session.container))
    session.docker_client.networks.get(session.network_name).remove()
