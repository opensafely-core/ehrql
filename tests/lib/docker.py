import sys

import docker
from docker.errors import ContainerError


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
