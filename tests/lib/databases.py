import os
import secrets
import time
from pathlib import Path

import sqlalchemy
import sqlalchemy.exc
from packaging.version import parse as version_parse
from requests.exceptions import ConnectionError  # noqa A004
from sqlalchemy.dialects import registry
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from trino.exceptions import TrinoQueryError

from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.utils.itertools_utils import iter_flatten
from tests.lib.orm_utils import SYNTHETIC_PRIMARY_KEY, table_has_one_row_per_patient


MSSQL_SETUP_DIR = Path(__file__).parents[1].absolute() / "support/mssql"
TRINO_SETUP_DIR = Path(__file__).parents[1].absolute() / "support/trino"


# Register our modified SQLAlchemy dialects
registry.register(
    "spark.pyhive.opensafely",
    "ehrql.query_engines.spark_dialect",
    "SparkDialect",
)
registry.register(
    "sqlite.pysqlite.opensafely",
    "ehrql.query_engines.sqlite_dialect",
    "SQLiteDialect",
)

registry.register(
    "trino.opensafely", "ehrql.query_engines.trino_dialect", "TrinoDialect"
)


class DbDetails:
    def __init__(
        self,
        protocol,
        driver,
        host_from_container,
        port_from_container,
        host_from_host,
        port_from_host,
        username="",
        password="",
        db_name="",
        query=None,
        temp_db=None,
        engine_kwargs=None,
        test_query="SELECT 1",
    ):
        self.protocol = protocol
        self.driver = driver
        self.host_from_container = host_from_container
        self.port_from_container = port_from_container
        self.host_from_host = host_from_host
        self.port_from_host = port_from_host
        self.password = password
        self.username = username
        self.db_name = db_name
        self.query = query
        self.temp_db = temp_db
        self.engine_kwargs = engine_kwargs or {}
        self.test_query = test_query

        self.metadata = None

    def container_url(self):
        return self._url(self.host_from_container, self.port_from_container)

    def host_url(self):
        return self._url(self.host_from_host, self.port_from_host)

    def engine(self, dialect=None, **kwargs):
        url = self._url(
            self.host_from_host, self.port_from_host, include_driver=bool(self.driver)
        )
        engine_url = sqlalchemy.engine.make_url(url)
        engine_kwargs = self.engine_kwargs | kwargs
        engine = sqlalchemy.create_engine(engine_url, **engine_kwargs)
        return engine

    def _url(self, host, port, include_driver=False):
        assert self.username
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        else:
            auth = f"{self.username}@"
        if include_driver:
            protocol = f"{self.protocol}+{self.driver}"
        else:
            protocol = self.protocol
        url = f"{protocol}://{auth}{host}:{port}/{self.db_name}"
        # only used for databricks atm
        if self.query:  # pragma: no cover
            url += "?" + "&".join(f"{k}={v}" for k, v in self.query.items())
        return url

    def setup(self, *input_data, metadata=None):
        """
        Accepts SQLAlchemy ORM objects (which may be arbitrarily nested within lists and
        tuples), creates the necessary tables and inserts them into the database
        """
        input_data = list(iter_flatten(input_data))
        engine = self.engine()
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()

        if metadata:
            pass
        elif input_data:
            metadata = input_data[0].metadata
        else:
            assert False, "No source of metadata"
        assert all(item.metadata is metadata for item in input_data)

        self.metadata = metadata
        metadata.create_all(engine)
        session.bulk_save_objects(
            input_data,
            return_defaults=False,
            update_changed_only=False,
            preserve_order=False,
        )

        if self.temp_db is not None:  # pragma: cover-spark-only
            session.execute(
                sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {self.temp_db}")
            )
        session.commit()

    def teardown(self):
        if self.metadata is not None:
            self.metadata.drop_all(self.engine())


def wait_for_database(database, timeout=20):
    engine = database.engine()
    start = time.time()
    limit = start + timeout
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(sqlalchemy.text(database.test_query))
            break
        except (
            sqlalchemy.exc.OperationalError,
            ConnectionRefusedError,
            ConnectionResetError,
            BrokenPipeError,
            ConnectionError,
            TrinoQueryError,
            sqlalchemy.exc.DBAPIError,
        ) as e:  # pragma: no cover
            if time.time() >= limit:
                raise Exception(
                    f"Failed to connect to database after {timeout} seconds: "
                    f"{engine.url}"
                ) from e
            time.sleep(1)


def make_mssql_database(containers):
    password = "Your_password123!"

    container_name = "ehrql-mssql"
    mssql_port = 1433

    if not containers.is_running(container_name):  # pragma: no cover
        run_mssql(container_name, containers, password, mssql_port)

    container_ip = containers.get_container_ip(container_name)
    host_mssql_port = containers.get_mapped_port_for_host(container_name, mssql_port)

    return DbDetails(
        protocol="mssql",
        driver="pymssql",
        host_from_container=container_ip,
        port_from_container=mssql_port,
        host_from_host="localhost",
        port_from_host=host_mssql_port,
        username="sa",
        password=password,
        db_name="test",
    )


def run_mssql(container_name, containers, password, mssql_port):  # pragma: no cover
    containers.run_bg(
        name=container_name,
        # This is *not* the version that TPP run for us in production which, as of
        # 2024-09-24, is SQL Server 2016 (13.0.5893.48). That version is not available
        # as a Docker image, so we run the oldest supported version instead. Both the
        # production server and our test server set the "compatibility level" to the
        # same value so the same feature set should be supported.
        image="mcr.microsoft.com/mssql/server:2019-CU28-ubuntu-20.04",
        volumes={
            MSSQL_SETUP_DIR: {"bind": "/mssql", "mode": "ro"},
        },
        # Choose an arbitrary free port to publish the MSSQL port on
        ports={mssql_port: None},
        environment={
            "MSSQL_SA_PASSWORD": password,
            "ACCEPT_EULA": "Y",
            "MSSQL_TCP_PORT": str(mssql_port),
            # Make all string comparisons case-sensitive across all databases
            "MSSQL_COLLATION": "SQL_Latin1_General_CP1_CS_AS",
        },
        user="root",
        entrypoint="/mssql/entrypoint.sh",
        command="/opt/mssql/bin/sqlservr",
    )


def make_spark_database(containers):  # pragma: cover-spark-only
    if "DATABRICKS_URL" in os.environ:  # pragma: no cover
        return make_databricks_database()
    else:
        return make_spark_container_database(containers)


def make_spark_container_database(containers):  # pragma: cover-spark-only
    container_name = "ehrql-spark"
    # This is the default anyway, but better to be explicit
    spark_port = 10001

    if not containers.is_running(container_name):  # pragma: no cover
        containers.run_bg(
            name=container_name,
            # This is the version of Spark that Graphnet use.
            image="docker.io/bitnamilegacy/spark:3.2.1-debian-11-r12",
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
                # These settings try to reduce the amount of unnecessary "Big Data" work
                # which Spark does on our tiny test queries in an attempt to speed them
                # up. They were suggested by a helpful StackOverflow user and seem to
                # give about a 20% speed up on the Spark tests:
                # https://stackoverflow.com/a/74878746
                "--conf",
                "spark.sql.shuffle.partitions=1",
                "--conf",
                "spark.sql.autoBroadcastJoinThreshold=-1",
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

    container_ip = containers.get_container_ip(container_name)
    host_spark_port = containers.get_mapped_port_for_host(container_name, spark_port)

    return DbDetails(
        protocol="spark",
        driver="pyhive+opensafely",
        host_from_container=container_ip,
        port_from_container=spark_port,
        host_from_host="localhost",
        port_from_host=host_spark_port,
        # These are arbitrary but we need to supply _some_ values here
        username="foo",
        password="bar",
        temp_db="tempdb",
    )


# This is not used by regular units tests, only by manual invocation, hence why
# coverage is skipped
def make_databricks_database():  # pragma: no cover
    url = os.environ["DATABRICKS_URL"]
    url = sqlalchemy.engine.make_url(url)

    return DbDetails(
        protocol="spark",
        driver="pyhive+opensafely",
        host_from_container=url.host,
        port_from_container=url.port or 443,
        host_from_host=url.host,
        port_from_host=url.port or 443,
        username=url.username,
        password=url.password,
        db_name=url.database,
        query=url.query,
        temp_db="tempdb",
    )


class InMemorySQLiteDatabase(DbDetails):
    def __init__(self):
        db_name = secrets.token_hex(8)
        super().__init__(
            db_name=db_name,
            protocol="sqlite",
            driver="pysqlite+opensafely",
            host_from_container=None,
            port_from_container=None,
            host_from_host=None,
            port_from_host=None,
            # QueuePool allows each connection to the shared cache
            # (see self._url) to have its own transactional state.
            # See https://sqlalche.me/e/21/sqmp
            engine_kwargs={"poolclass": QueuePool},
        )
        self._engine = None

    def engine(self, dialect=None, **kwargs):
        # We need to hold a reference to the engine for the lifetime of this database to stop the contents of the
        # database from being garbage-collected.
        if not self._engine:
            self._engine = super().engine(dialect, **kwargs)
        return self._engine

    def _url(self, host, port, include_driver=False):
        if include_driver:
            protocol = f"{self.protocol}+{self.driver}"
        else:
            protocol = self.protocol
        # https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#uri-connections
        # https://sqlite.org/inmemorydb.html
        return f"{protocol}:///file:{self.db_name}?mode=memory&cache=shared&uri=true"


class InMemoryPythonDatabase:
    def __init__(self):
        self.database = InMemoryDatabase()

    def setup(self, *input_data, metadata=None):
        """
        Behaves like `DbDetails.setup` in taking a iterator of ORM instances but
        translates these into the sort of objects needed by the `InMemoryDatabase`
        """
        input_data = list(iter_flatten(input_data))

        if metadata:
            pass
        elif input_data:
            metadata = input_data[0].metadata
        else:
            assert False, "No source of metadata"
        assert all(item.metadata is metadata for item in input_data)

        sqla_table_to_items = {table: [] for table in metadata.sorted_tables}
        for item in input_data:
            sqla_table_to_items[item.__table__].append(item)

        for sqla_table, items in sqla_table_to_items.items():
            columns = [
                c.name for c in sqla_table.columns if c.name != SYNTHETIC_PRIMARY_KEY
            ]
            self.database.add_table(
                name=sqla_table.name,
                one_row_per_patient=table_has_one_row_per_patient(sqla_table),
                columns=columns,
                rows=[[getattr(item, c) for c in columns] for item in items],
            )

    def teardown(self):
        self.database.populate({})

    def host_url(self):
        # Where other query engines expect a DSN string to connect to the database the
        # InMemoryQueryEngine expects a reference to the database object itself
        return self.database


def make_trino_database(containers):
    container_name = "ehrql-trino"
    trino_port = 8080

    if not containers.is_running(container_name):  # pragma: no cover
        run_trino(container_name, containers, trino_port)

    container_ip = containers.get_container_ip(container_name)
    host_trino_port = containers.get_mapped_port_for_host(container_name, trino_port)

    return DbDetails(
        protocol="trino",
        driver="opensafely",
        host_from_container=container_ip,
        port_from_container=trino_port,
        host_from_host="localhost",
        port_from_host=host_trino_port,
        username="trino",
        db_name="trino/default",
        # Disable automatic retries for the test client: it's pointless and creates log
        # noise
        engine_kwargs={"connect_args": {"max_attempts": 1}},
        # This schema doesn't exist by default, so if it does then we know our setup SQL
        # has finished running
        test_query="SHOW CREATE SCHEMA trino",
    )


def run_trino(container_name, containers, trino_port):  # pragma: no cover
    # Note, I don't actually know that this is the minimum required version of Docker
    # Engine. I do know that 20.10.5 is unsupported (because that's what I had
    # installed) and that 20.10.16 is supported, according to this comment:
    # https://github.com/adoptium/containers/issues/214#issuecomment-1139464798 which
    # was linked from this issue: https://github.com/trinodb/trino/issues/14269
    min_docker_version = "20.10.16"
    docker_version = containers.get_engine_version()
    assert version_parse(docker_version) >= version_parse(min_docker_version), (
        f"The Trino Docker image requires Docker Engine v{min_docker_version}"
        f" or above but you have v{docker_version}"
    )
    containers.run_bg(
        name=container_name,
        # This is the version which happened to be current at the time of writing and is
        # pinned for reproduciblity's sake rather than because there's anything
        # significant about it
        image="trinodb/trino:440",
        volumes={
            TRINO_SETUP_DIR: {"bind": "/trino", "mode": "ro"},
            f"{TRINO_SETUP_DIR}/etc": {"bind": "/etc/trino", "mode": "ro"},
        },
        # Choose an arbitrary free port to publish the trino port on
        ports={trino_port: None},
        environment={},
        user="root",
        entrypoint="/trino/entrypoint.sh",
        command="/usr/lib/trino/bin/run-trino",
    )
