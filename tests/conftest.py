from pathlib import Path

import docker
import docker.errors
import pytest
from lib import mock_backend
from lib.databases import make_database, make_spark_database, wait_for_database
from lib.databricks_schema import Base as DatabricksBase
from lib.docker import Containers
from lib.graphnet_schema import Base as GraphnetBase
from lib.tpp_schema import Base as TppBase
from lib.util import iter_flatten
from sqlalchemy.orm import sessionmaker

from cohortextractor.definition.base import cohort_registry


BASES = {"tpp": TppBase, "graphnet": GraphnetBase, "databricks": DatabricksBase}


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


@pytest.fixture(scope="session")
def database(request, containers, docker_client, network, mssql_dir):
    try:
        database = request.session.database
    except AttributeError:
        database = make_database(containers, docker_client, mssql_dir)
        wait_for_database(database)
        request.session.database = database
    yield database


@pytest.fixture
def setup_test_database(database):
    def setup(input_data, base=mock_backend.Base):
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


@pytest.fixture(scope="session")
def spark_database(containers, network):
    database = make_spark_database(containers, network)
    wait_for_database(database, timeout=15)
    yield database


@pytest.fixture
def setup_spark_database(spark_database):
    def setup(*input_data, backend=None):
        base = BASES[backend]
        # Create engine
        engine = spark_database.engine()
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


@pytest.fixture(autouse=True)
def cleanup_register():
    yield
    cohort_registry.reset()
