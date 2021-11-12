import sys

import docker
from docker.errors import ContainerError


class Containers:
    def __init__(self, docker_client):
        self._docker = docker_client

    def get_container(self, name):
        return self._docker.containers.get(name)

    def is_running(self, name):
        try:
            container = self.get_container(name)
            return container.status == "running"  # pragma: no cover
        except docker.errors.NotFound:  # pragma: no cover
            return False

    def get_mapped_port_for_host(self, name, container_port):
        """
        Given a port on a container return the port on the host to which it is
        mapped
        """
        assert isinstance(container_port, int)
        container_port = f"{container_port}/tcp"
        container = self.get_container(name)
        port_config = container.attrs["NetworkSettings"]["Ports"][container_port]
        host_port = port_config[0]["HostPort"]
        return host_port

    def get_container_ip(self, name):
        """
        Given a container name, return it IP address
        """
        container = self.get_container(name)
        return container.attrs["NetworkSettings"]["IPAddress"]

    # All available arguments documented here:
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    def run_bg(self, name, image, **kwargs):  # pragma: no cover
        return self._run(name=name, image=image, detach=True, **kwargs)

    # All available arguments documented here:
    # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    def run_fg(self, image, **kwargs):
        try:
            output = self._run(image=image, detach=False, stderr=True, **kwargs)
            print(str(output, "utf-8"))
        except ContainerError as e:  # pragma: no cover
            print(str(e.stderr, "utf-8"), file=sys.stderr)
            raise

    def _run(self, **kwargs):
        return self._docker.containers.run(remove=True, **kwargs)
