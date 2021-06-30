import sys
from pathlib import Path

import docker
import pytest
from docker.errors import ContainerError


class Study:
    def __init__(self, study_path):
        super().__init__()
        self._path = Path(__file__).parent.absolute() / "fixtures" / study_path

    def tables(self):
        return self._path / "tables.sql"

    def study_definition(self):
        return self._path / "study_definition.py"

    def expected_results(self):
        return self._path / "results.csv"


@pytest.fixture
def load_study():
    def read_dir(path):
        return Study(path)

    return read_dir


@pytest.fixture
def docker_client():
    yield docker.from_env()


@pytest.fixture
def network(docker_client):
    name = "test_network"
    docker_client.networks.create(name)
    yield name
    docker_client.networks.get(name).remove()


class Containers:
    def __init__(self, docker_client):
        self._docker = docker_client

    def is_running(self, name):
        try:
            container = self._docker.containers.get(name)
            return container.status == "running"
        except docker.errors.NotFound:
            return False

    # All available arguments documented here:
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    def run_bg(self, name, image, **kwargs):
        return self._run(name=name, image=image, detach=True, **kwargs)

    # All available arguments documented here:
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    def run_fg(self, image, **kwargs):
        try:
            output = self._run(image=image, detach=False, stderr=True, **kwargs)
            print(str(output, "utf-8"))
        except ContainerError as e:
            print(str(e.stderr, "utf-8"), file=sys.stderr)
            raise

    # noinspection PyMethodMayBeStatic
    def destroy(self, container):
        container.remove(force=True)

    def _run(self, **kwargs):
        return self._docker.containers.run(remove=True, **kwargs)


@pytest.fixture
def containers(docker_client, network):
    # `network` is specified as an argument for sequencing reasons. We need to make sure that the network is created
    # before containers that use it and that all containers are cleaned up before the network is removed.
    yield Containers(docker_client)


@pytest.fixture
def run_container(containers):
    container = None

    def run(**kwargs):
        nonlocal container
        container = containers.run_bg(**kwargs)

    yield run
    if container:
        # noinspection PyTypeChecker
        containers.destroy(container)
