import pytest

from databuilder.definition.base import dataset_registry
from databuilder.query_engines.mssql import MssqlQueryEngine
from databuilder.query_engines.spark import SparkQueryEngine

from .lib.databases import make_database, make_spark_database, wait_for_database
from .lib.docker import Containers
from .lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
from .lib.mock_backend import backend_factory
from .lib.study import Study
from .lib.util import extract


# Fail the build if we see any warnings.
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if terminalreporter.stats.get("warnings"):  # pragma: no cover
        print("ERROR: warnings detected")
        if terminalreporter._session.exitstatus == 0:
            terminalreporter._session.exitstatus = 13


@pytest.fixture(scope="session")
def containers():
    yield Containers()


@pytest.fixture(scope="session")
def database(containers):
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
    dataset_registry.reset()


class QueryEngineFixture:
    def __init__(self, name, database, query_engine_class):
        self.name = name
        self.database = database
        self.query_engine_class = query_engine_class
        self.backend = backend_factory(query_engine_class)

    def setup(self, *items):
        return self.database.setup(*items)

    def extract(self, dataset, **kwargs):
        results = extract(dataset, self.backend, self.database, **kwargs)
        # We don't explicitly order the results and not all databases naturally return
        # in the same order
        results.sort(key=lambda i: i["patient_id"])
        return results

    def sqlalchemy_engine(self, **kwargs):
        return self.database.engine(
            dialect=self.query_engine_class.sqlalchemy_dialect, **kwargs
        )


@pytest.fixture(
    scope="session", params=["mssql", pytest.param("spark", marks=pytest.mark.spark)]
)
def engine(request, database, spark_database):
    name = request.param
    if name == "mssql":
        return QueryEngineFixture(name, database, MssqlQueryEngine)
    elif name == "spark":
        return QueryEngineFixture(name, spark_database, SparkQueryEngine)
    else:
        assert False


@pytest.fixture
def in_memory_engine():
    return QueryEngineFixture("in_memory", InMemoryDatabase(), InMemoryQueryEngine)


@pytest.fixture
def study(tmp_path, monkeypatch, containers):
    return Study(tmp_path, monkeypatch, containers)
