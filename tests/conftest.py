import docker
import docker.errors
import pytest

from cohortextractor.concepts import tables
from cohortextractor.definition import Cohort, exists
from cohortextractor.definition.base import cohort_registry

from .lib.databases import make_database, make_spark_database, wait_for_database
from .lib.docker import Containers


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
