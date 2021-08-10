import random
import time

import docker.errors
import sqlalchemy
import sqlalchemy.exc
from lib.util import get_mode


DEFAULT_MSSQL_PORT = 1433


class DbDetails:
    def __init__(
        self,
        network,
        host_from_container,
        port_from_container,
        host_from_host,
        port_from_host,
        password,
        db_name,
    ):
        self.network = network
        self.host_from_container = host_from_container
        self.port_from_container = port_from_container
        self.host_from_host = host_from_host
        self.port_from_host = port_from_host
        self.password = password
        self.db_name = db_name

    def host_url(self):
        return self._url(self.host_from_host, self.port_from_host)

    def container_url(self):
        return self._url(self.host_from_container, self.port_from_container)

    def engine(self, echo=True, **kwargs):
        engine_url = sqlalchemy.engine.make_url(self.host_url())
        engine_url = engine_url.set(drivername="mssql+pymssql")
        # We always want the "future" API, we usually want to echo queries
        return sqlalchemy.create_engine(engine_url, future=True, echo=echo, **kwargs)

    def _url(self, host, port):
        return f"mssql://SA:{self.password}@{host}:{port}/{self.db_name}"


def null_database():
    return DbDetails(None, None, None, None, None, None, None)


def make_database(containers, docker_client, mssql_dir, network):
    password = "Your_password123!"

    if database_mode() == "persistent":
        return persistent_database(containers, password, docker_client, mssql_dir)
    if database_mode() == "ephemeral":
        return ephemeral_database(containers, password, mssql_dir, network)


def wait_for_database(database):
    engine = database.engine(echo=False)

    start = time.time()
    timeout = 10
    limit = start + timeout
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(sqlalchemy.text("SELECT 'hello'"))
            break
        except sqlalchemy.exc.OperationalError as e:
            if time.time() >= limit:
                raise Exception(
                    f"Failed to connect to mssql after {timeout} seconds"
                ) from e
            time.sleep(1)


def database_mode():
    return get_mode("DATABASE", ["persistent", "ephemeral"], "persistent")


PERSISTENT_DATABASE_PORT = 49152


def persistent_database(containers, password, docker_client, mssql_dir):
    container = "cohort-extractor-mssql"
    network = "cohort-extractor-network"
    published_port = PERSISTENT_DATABASE_PORT

    try:
        docker_client.networks.get(network)
    except docker.errors.NotFound:
        docker_client.networks.create(network)

    if not containers.is_running(container):
        run_mssql(container, containers, mssql_dir, network, password, published_port)

    return None, DbDetails(
        network=network,
        host_from_container=container,
        port_from_container=DEFAULT_MSSQL_PORT,
        host_from_host="localhost",
        port_from_host=published_port,
        password=password,
        db_name="test",
    )


def ephemeral_database(containers, password, mssql_dir, network):
    container = "mssql"
    published_port = random.randint(PERSISTENT_DATABASE_PORT + 1, 65535)

    run_mssql(container, containers, mssql_dir, network, password, published_port)

    return container, DbDetails(
        network=network,
        host_from_container=container,
        port_from_container=DEFAULT_MSSQL_PORT,
        host_from_host="localhost",
        port_from_host=published_port,
        password=password,
        db_name="test",
    )


def run_mssql(container_name, containers, mssql_dir, network, password, published_port):
    containers.run_bg(
        name=container_name,
        image="mcr.microsoft.com/mssql/server:2017-CU25-ubuntu-16.04",
        volumes={
            mssql_dir: {"bind": "/mssql", "mode": "ro"},
        },
        network=network,
        ports={f"{DEFAULT_MSSQL_PORT}/TCP": published_port},
        environment={"SA_PASSWORD": password, "ACCEPT_EULA": "Y"},
        entrypoint="/mssql/entrypoint.sh",
        command="/opt/mssql/bin/sqlservr",
    )
