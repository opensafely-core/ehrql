import pytest

from databuilder.definition.base import dataset_registry
from databuilder.query_engines.mssql import MSSQLQueryEngine
from databuilder.query_engines.spark import SparkQueryEngine
from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_language import compile

from .lib.databases import (
    InMemorySQLiteDatabase,
    make_mssql_database,
    make_spark_database,
    wait_for_database,
)
from .lib.docker import Containers
from .lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
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
def mssql_database(containers):
    database = make_mssql_database(containers)
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

    def setup(self, *items, metadata=None):
        return self.database.setup(*items, metadata=metadata)

    def extract(self, dataset, **engine_kwargs):
        variables = compile(dataset)
        return self.extract_qm(variables, **engine_kwargs)

    def extract_qm(self, variables, **engine_kwargs):
        query_engine = self.query_engine_class(
            self.database.host_url(), **engine_kwargs
        )
        with query_engine.execute_query(variables) as results:
            # We don't explicitly order the results and not all databases naturally
            # return in the same order
            return sorted(map(dict, results), key=lambda i: i["patient_id"])

    def sqlalchemy_engine(self):
        return self.query_engine_class(self.database.host_url()).engine


@pytest.fixture(scope="session")
def in_memory_sqlite_database():
    return InMemorySQLiteDatabase()


@pytest.fixture(params=["in_memory", "sqlite", "mssql", "spark"])
def engine(request, in_memory_sqlite_database, mssql_database, spark_database):
    name = request.param
    if name == "in_memory":
        # There are some tests we currently expect to fail against the in-memory engine
        marks = [m.name for m in request.node.iter_markers()]
        if "xfail_in_memory" in marks:
            pytest.xfail()
        return QueryEngineFixture(name, InMemoryDatabase(), InMemoryQueryEngine)
    elif name == "sqlite":
        return QueryEngineFixture(name, in_memory_sqlite_database, SQLiteQueryEngine)
    elif name == "mssql":
        return QueryEngineFixture(name, mssql_database, MSSQLQueryEngine)
    elif name == "spark":
        return QueryEngineFixture(name, spark_database, SparkQueryEngine)
    else:
        assert False


@pytest.fixture
def study(tmp_path, monkeypatch, containers):
    return Study(tmp_path, monkeypatch, containers)
