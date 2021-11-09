import time

import docker.errors
import sqlalchemy
import sqlalchemy.exc

from cohortextractor.sqlalchemy_drivers import set_driver


DEFAULT_MSSQL_PORT = 1433


class DbDetails:
    def __init__(
        self,
        network,
        protocol,
        host_from_container,
        port_from_container,
        host_from_host,
        port_from_host,
        username="",
        password="",
        db_name="",
    ):
        self.network = network
        self.protocol = protocol
        self.host_from_container = host_from_container
        self.port_from_container = port_from_container
        self.host_from_host = host_from_host
        self.port_from_host = port_from_host
        self.password = password
        self.username = username
        self.db_name = db_name

    def host_url(self):
        return self._url(self.host_from_host, self.port_from_host)

    def container_url(self):
        return self._url(self.host_from_container, self.port_from_container)

    def engine(self, **kwargs):
        engine_url = sqlalchemy.engine.make_url(self.host_url())
        engine_url = set_driver(engine_url)
        # We always want the "future" API
        return sqlalchemy.create_engine(engine_url, future=True, **kwargs)

    def _url(self, host, port):
        if self.username or self.password:
            auth = f"{self.username}:{self.password}@"
        else:
            auth = ""
        return f"{self.protocol}://{auth}{host}:{port}/{self.db_name}"


def null_database():
    return DbDetails(None, None, None, None, None, None)


def make_database(containers, docker_client, mssql_dir):
    password = "Your_password123!"

    container = "cohort-extractor-mssql"
    network = "cohort-extractor-network"
    published_port = PERSISTENT_DATABASE_PORT
    try:
        docker_client.networks.get(network)
    except docker.errors.NotFound:
        docker_client.networks.create(network)
    if not containers.is_running(container):
        run_mssql(container, containers, mssql_dir, network, password, published_port)
    return DbDetails(
        network=network,
        protocol="mssql",
        host_from_container=container,
        port_from_container=DEFAULT_MSSQL_PORT,
        host_from_host="localhost",
        port_from_host=published_port,
        username="SA",
        password=password,
        db_name="test",
    )


def wait_for_database(database, timeout=10):
    engine = database.engine()

    start = time.time()
    limit = start + timeout
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(sqlalchemy.text("SELECT 'hello'"))
            break
        except (
            sqlalchemy.exc.OperationalError,
            ConnectionRefusedError,
            ConnectionResetError,
            BrokenPipeError,
        ) as e:
            if time.time() >= limit:
                raise Exception(
                    f"Failed to connect to database after {timeout} seconds: "
                    f"{engine.url}"
                ) from e
            time.sleep(1)


PERSISTENT_DATABASE_PORT = 49152


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


def make_spark_database(containers, network):
    container_name = "cohort-extractor-spark"
    # This is the default anyway, but better to be explicit
    spark_port = 10001

    if not containers.is_running(container_name):
        containers.run_bg(
            name=container_name,
            # Nothing special about this particular version other than that
            # it's the latest as of the time of writing
            image="docker.io/bitnami/spark:3.1.2-debian-10-r126",
            entrypoint="/bin/bash",
            command=[
                # To speak SQL to our Spark database we need to start a thing
                # called Hive which speaks a protocol called Thrift. Command
                # below cribbed from:
                # https://github.com/bitnami/bitnami-docker-spark/issues/32#issuecomment-820668226
                "/opt/bitnami/spark/bin/spark-submit",
                "--class",
                "org.apache.spark.sql.hive.thriftserver.HiveThriftServer2",
                # By default Hive tries to set cookies on the client which
                # breaks both the client libraries I've tried so we disable
                # that here
                "--hiveconf",
                "hive.server2.thrift.http.cookie.auth.enabled=false",
                # Use the HTTP (as opposed to binary) protocol
                "--hiveconf",
                "hive.server2.transport.mode=http",
                "--hiveconf",
                f"hive.server2.thrift.http.port={spark_port}",
            ],
            # As described below, there's a directory permissions issue when
            # trying to run Hive using this container. It's possible to chmod
            # the relevant directory, but given that this is a test environment
            # it's easier just to run as root. See:
            # https://github.com/bitnami/bitnami-docker-spark/issues/32
            user="root",
            # Supplying a host port of None tells Docker to choose an arbitrary
            # free port
            ports={spark_port: None},
        )

    host_spark_port = containers.get_mapped_port_for_host(container_name, spark_port)

    return DbDetails(
        network=network,
        protocol="spark",
        host_from_container=container_name,
        port_from_container=spark_port,
        host_from_host="localhost",
        port_from_host=host_spark_port,
        # These are arbitrary but we need to supply _some_ values here
        username="foo",
        password="bar",
    )
