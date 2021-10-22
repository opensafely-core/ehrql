from contextlib import contextmanager
from pathlib import Path

import docker
import docker.errors
import pytest
from lib import mock_backend, playback
from lib.databases import DbDetails, make_database, wait_for_database
from lib.docker import Containers
from lib.graphnet_schema import Base as GraphnetBase
from lib.tpp_schema import Base as TppBase
from lib.util import iter_flatten
from sqlalchemy.orm import sessionmaker


BASES = {"tpp": TppBase, "graphnet": GraphnetBase}


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
def network(docker_client):
    name = "test_network"
    docker_client.networks.create(name)
    yield name
    docker_client.networks.get(name).remove()


@pytest.fixture(scope="session")
def containers(docker_client):
    yield Containers(docker_client)


@pytest.fixture(scope="session")
def mssql_dir():
    yield Path(__file__).parent.absolute() / "support/mssql"


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
    identifier = f"{test_module}.{test_name}"
    return identifier


@pytest.fixture(scope="session")
def real_db(containers, docker_client, network, mssql_dir, request):
    container = None

    def lazily_created_session_scoped_database(recording):
        nonlocal container
        try:
            database = request.session.database
        except AttributeError:
            container, database = make_database(
                containers, docker_client, mssql_dir, network
            )
            with recording.suspended():
                wait_for_database(database)
            request.session.database = database
        return database

    yield lazily_created_session_scoped_database

    if container is not None:
        containers.destroy(containers.get_container(container))


@pytest.fixture(scope="session")
def dummy_db():
    yield DbDetails("", "", 0, "", 0, "", "")


@pytest.fixture
def database(request, real_db, dummy_db, recording):
    assert is_smoke_test(request) or is_integration_test(
        request
    ), "Only smoke and integration tests can use the database"
    assert not (
        is_smoke_test(request) and is_integration_test(request)
    ), "A test cannot be both a smoke test and an integration test"

    if is_smoke_test(request) or recording.mode == "record":
        yield real_db(recording)
    else:
        yield dummy_db


@pytest.fixture
def setup_test_database(database, recording, request):
    def setup(input_data, base=mock_backend.Base):
        if is_integration_test(request) and recording.mode == "playback":
            # Since we suspend recording during setup, we must skip it altogether during playback.
            return

        with recording.suspended():
            # Create engine
            engine = database.engine()
            # Reset the schema
            base.metadata.drop_all(engine)
            base.metadata.create_all(engine)
            # Create session
            Session = sessionmaker()
            Session.configure(bind=engine)
            session = Session()
            # Load test data
            session.bulk_save_objects(iter_flatten(input_data))
            session.commit()

    return setup


@pytest.fixture
def setup_backend_database(setup_test_database):
    def setup(*data, backend="tpp"):
        setup_test_database(data, base=BASES[backend])

    yield setup
