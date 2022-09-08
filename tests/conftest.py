import os
import subprocess
from pathlib import Path

import pytest

import databuilder
from databuilder.main import get_sql_strings
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
        results = query_engine.get_results(variables)
        # We don't explicitly order the results and not all databases naturally
        # return in the same order
        return sorted(map(dict, results), key=lambda i: i["patient_id"])

    def dump_dataset_sql(self, dataset, **engine_kwargs):
        variables = compile(dataset)
        query_engine = self.query_engine_class(dsn=None, **engine_kwargs)
        return get_sql_strings(query_engine, variables)

    def sqlalchemy_engine(self):
        return self.query_engine_class(self.database.host_url()).engine


@pytest.fixture(scope="session")
def in_memory_sqlite_database():
    return InMemorySQLiteDatabase()


QUERY_ENGINE_NAMES = ("in_memory", "sqlite", "mssql", "spark")


def engine_factory(request, engine_name):
    # We dynamically request fixtures rather than making them arguments in the usual way
    # so that we only start the database containers we actually need for the test run
    fixture = request.getfixturevalue

    if engine_name == "in_memory":
        return QueryEngineFixture(engine_name, InMemoryDatabase(), InMemoryQueryEngine)
    elif engine_name == "sqlite":
        return QueryEngineFixture(
            engine_name, fixture("in_memory_sqlite_database"), SQLiteQueryEngine
        )
    elif engine_name == "mssql":
        return QueryEngineFixture(
            engine_name, fixture("mssql_database"), MSSQLQueryEngine
        )
    elif engine_name == "spark":
        return QueryEngineFixture(
            engine_name, fixture("spark_database"), SparkQueryEngine
        )
    else:
        assert False


@pytest.fixture(params=QUERY_ENGINE_NAMES)
def engine(request):
    return engine_factory(request, request.param)


@pytest.fixture(scope="session")
def databuilder_image():
    project_dir = Path(databuilder.__file__).parents[1]
    # Note different name from production image to avoid confusion
    image = "databuilder-dev"
    # We're deliberately choosing to shell out to the docker client here rather than use
    # the docker-py library to avoid possible difference in the build process (docker-py
    # doesn't seem to be particularly actively maintained)
    subprocess.run(
        ["docker", "build", project_dir, "-t", image],
        check=True,
        env=os.environ | {"DOCKER_BUILDKIT": "1"},
    )
    return f"{image}:latest"


@pytest.fixture
def study(tmp_path, containers, databuilder_image):
    return Study(tmp_path, containers, databuilder_image)
