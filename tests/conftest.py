import docker
import docker.errors
import pytest

from cohortextractor.concepts import tables
from cohortextractor.definition import Cohort, exists
from cohortextractor.definition.base import cohort_registry
from cohortextractor.query_engines.mssql import MssqlQueryEngine
from cohortextractor.query_engines.spark import SparkQueryEngine

from .lib.databases import make_database, make_spark_database, wait_for_database
from .lib.docker import Containers
from .lib.mock_backend import backend_factory
from .lib.util import extract


@pytest.fixture(scope="session")
def docker_client():
    yield docker.from_env()


@pytest.fixture(scope="session")
def containers(docker_client):
    yield Containers(docker_client)


@pytest.fixture(scope="session")
def database(request, containers):
    database = make_database(containers)
    wait_for_database(database)
    yield database


@pytest.fixture(scope="session")
def spark_database(containers):
    database = make_spark_database(containers)
    wait_for_database(database, timeout=15)
    yield database


@pytest.fixture(autouse=True)
def cleanup_register():
    yield
    cohort_registry.reset()


@pytest.fixture
def cohort_with_population():
    cohort = Cohort()
    registrations_table = tables.registrations
    registered = registrations_table.select_column(
        registrations_table.patient_id
    ).make_one_row_per_patient(exists)
    cohort.set_population(registered)
    yield cohort


class QueryEngineFixture:
    def __init__(self, name, database, query_engine_class):
        self.name = name
        self.database = database
        self.query_engine_class = query_engine_class
        self.backend = backend_factory(query_engine_class)

    def setup(self, *items):
        return self.database.setup(*items)

    def extract(self, cohort, **kwargs):
        results = extract(cohort, self.backend, self.database, **kwargs)
        # We don't explicitly order the results and not all databases naturally return
        # in the same order
        results.sort(key=lambda i: i["patient_id"])
        return results

    def sqlalchemy_engine(self, **kwargs):
        sqlalchemy_engine = self.database.engine(**kwargs)
        sqlalchemy_engine.dialect = self.query_engine_class.sqlalchemy_dialect()
        return sqlalchemy_engine


@pytest.fixture(scope="session", params=["mssql", "spark"])
def engine(request, database, spark_database):
    name = request.param
    if name == "mssql":
        return QueryEngineFixture(name, database, MssqlQueryEngine)
    elif name == "spark":
        return QueryEngineFixture(name, spark_database, SparkQueryEngine)
    else:
        assert False
