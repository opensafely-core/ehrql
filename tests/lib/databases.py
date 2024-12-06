import secrets
import time
from pathlib import Path

import sqlalchemy
import sqlalchemy.exc
from packaging.version import parse as version_parse
from requests.exceptions import ConnectionError  # noqa A004
from sqlalchemy.dialects import registry
from sqlalchemy.orm import sessionmaker
from trino.exceptions import TrinoQueryError

from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.utils.itertools_utils import iter_flatten
from tests.lib.orm_utils import SYNTHETIC_PRIMARY_KEY, table_has_one_row_per_patient


MSSQL_SETUP_DIR = Path(__file__).parents[1].absolute() / "support/mssql"
TRINO_SETUP_DIR = Path(__file__).parents[1].absolute() / "support/trino"


# Register our modified SQLAlchemy dialects
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
                connection.execute(sqlalchemy.text("SELECT 'hello'"))
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
