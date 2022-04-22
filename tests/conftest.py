import pytest

from databuilder import main
from databuilder.definition.base import dataset_registry
from databuilder.query_engines.mssql import MssqlQueryEngine
from databuilder.query_engines.spark import SparkQueryEngine
from databuilder.query_engines.sqlite import SQLiteQueryEngine

from .lib.databases import (
    InMemorySQLiteDatabase,
    make_database,
    make_spark_database,
    wait_for_database,
)
from .lib.docker import Containers
from .lib.mock_backend import backend_factory
from .lib.study import Study


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

    def extract(self, dataset, **backend_kwargs):
        results = list(
            main.extract(
                dataset, self.backend(self.database.host_url(), **backend_kwargs)
            )
        )
        # We don't explicitly order the results and not all databases naturally return
        # in the same order
        results.sort(key=lambda i: i["patient_id"])
        return results

    def extract_qm(self, variables):
        with self._execute(variables) as results:
            result = list(dict(row) for row in results)
            result.sort(key=lambda i: i["patient_id"])  # ensure stable ordering
            return result

    def _execute(self, variables):
        return self._build_engine(variables).execute_query()

    def _build_engine(self, variables):
        backend = self.backend(self.database.host_url())
        return backend.query_engine_class(variables, backend)

    def sqlalchemy_engine(self, **kwargs):
        return self.database.engine(
            dialect=self.query_engine_class.sqlalchemy_dialect, **kwargs
        )


@pytest.fixture(
    scope="session",
    params=["mssql", pytest.param("spark", marks=pytest.mark.spark), "sqlite"],
)
def engine(request, database, spark_database):
    name = request.param
    if name == "mssql":
        return QueryEngineFixture(name, database, MssqlQueryEngine)
    elif name == "spark":
        return QueryEngineFixture(name, spark_database, SparkQueryEngine)
    elif name == "sqlite":
        return QueryEngineFixture(name, InMemorySQLiteDatabase(), SQLiteQueryEngine)
    else:
        assert False


@pytest.fixture
def study(tmp_path, monkeypatch, containers):
    return Study(tmp_path, monkeypatch, containers)
