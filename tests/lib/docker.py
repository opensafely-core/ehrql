import os

from docker.errors import ContainerError, NotFound

import docker


__all__ = ["ContainerError", "Containers"]


class Containers:
    def __init__(self):
        self._docker = docker.from_env()

    def get_engine_version(self):  # pragma: no cover
        versions = self._docker.version()
        engine_details = [c for c in versions["Components"] if c["Name"] == "Engine"]
        assert len(engine_details) == 1
        return engine_details[0]["Version"]

    def get_container(self, name):
        return self._docker.containers.get(name)

    def is_running(self, name):
        try:
            container = self.get_container(name)
            return container.status == "running"  # pragma: no cover
        except NotFound:  # pragma: no cover
            return False

    def get_mapped_port_for_host(self, name, container_port):
        """
        Given a port on a container return the port on the host to which it is
        mapped
        """
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
    def run_captured(self, image, **kwargs):
        return self._run(image=image, detach=False, stdout=True, stderr=True, **kwargs)

    def _run(self, **kwargs):  # pragma: no cover
        # Run as non-root by default to match production
        kwargs.setdefault("user", os.getuid())
        return self._docker.containers.run(remove=True, **kwargs)
