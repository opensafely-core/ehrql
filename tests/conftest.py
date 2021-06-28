import sys
from pathlib import Path

import docker
import pytest
from docker.errors import ContainerError


class Study:
    def __init__(self, study_path):
        super().__init__()
        self._path = Path(__file__).parent.absolute() / "fixtures" / study_path

    def grab_tables(self):
        return self._path / "tables.sql"

    def grab_study_definition(self):
        return self._path / "study_definition.py"

    def grab_expected_results(self):
        return self._path / "results.csv"


@pytest.fixture
def study():
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
    def __init__(self, docker_client, network):
        self._docker = docker_client
        self._network = network

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

    def destroy(self, container):
        container.remove(force=True)

    def _run(self, **kwargs):
        return self._docker.containers.run(remove=True, network=self._network, **kwargs)


@pytest.fixture
def containers(docker_client, network):
    cs = Containers(docker_client, network)
    yield cs


@pytest.fixture
def run_container(containers):
    container = None

    def run(**kwargs):
        nonlocal container
        container = containers.run_bg(**kwargs)

    yield run
    if container:
        containers.destroy(container)
