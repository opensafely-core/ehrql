from pathlib import Path

import docker
import docker.errors
import pytest
from sqlalchemy.orm import sessionmaker

from cohortextractor.definition.base import cohort_registry

from .lib.databases import make_database, make_spark_database, wait_for_database
from .lib.docker import Containers
from .lib.util import iter_flatten


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
def containers(docker_client):
    yield Containers(docker_client)


@pytest.fixture(scope="session")
def mssql_dir():
    yield Path(__file__).parent.absolute() / "support/mssql"


@pytest.fixture(scope="session")
def database(request, containers, mssql_dir):
    try:
        database = request.session.database
    except AttributeError:
        database = make_database(containers, mssql_dir)
        wait_for_database(database)
        request.session.database = database
    yield database


@pytest.fixture
def setup_test_database(database):
    def setup(input_data):
        input_data = list(iter_flatten(input_data))
        # Create engine
        engine = database.engine()
        # Reset the schema
        metadata = input_data[0].metadata
        assert all(item.metadata is metadata for item in input_data)
        metadata.drop_all(engine)
        metadata.create_all(engine)
        # Create session
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        # Load test data
        session.bulk_save_objects(input_data)
        session.commit()

    return setup


@pytest.fixture
def setup_backend_database(setup_test_database):
    def setup(*data, backend=None):
        setup_test_database(data)

    yield setup


@pytest.fixture(scope="session")
def spark_database(containers):
    database = make_spark_database(containers)
    wait_for_database(database, timeout=15)
    yield database


@pytest.fixture
def setup_spark_database(spark_database):
    def setup(*input_data, backend=None):
        input_data = list(iter_flatten(input_data))
        # Create engine
        engine = spark_database.engine()
        # Reset the schema
        metadata = input_data[0].metadata
        assert all(item.metadata is metadata for item in input_data)
        metadata.drop_all(engine)
        metadata.create_all(engine)
        # Create session
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        # Load test data
        session.bulk_save_objects(input_data)
        session.commit()

    return setup


@pytest.fixture(autouse=True)
def cleanup_register():
    yield
    cohort_registry.reset()
