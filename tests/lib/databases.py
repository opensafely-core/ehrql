import secrets
import time
from pathlib import Path

import sqlalchemy
import sqlalchemy.exc
from requests.exceptions import ConnectionError
from sqlalchemy.dialects import registry
from sqlalchemy.orm import sessionmaker
from trino.exceptions import TrinoQueryError

from ehrql.utils.itertools_utils import iter_flatten


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
        self.metadata = None

    def container_url(self):
        return self._url(self.host_from_container, self.port_from_container)

    def host_url(self):
        return self._url(self.host_from_host, self.port_from_host)

    def engine(self, dialect=None, **kwargs):
        url = self._url(
            self.host_from_host,
            self.port_from_host,
            include_driver=True if self.driver else False,
        )
        engine_url = sqlalchemy.engine.make_url(url)
        engine = sqlalchemy.create_engine(engine_url, **kwargs)
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
        session.bulk_save_objects(input_data)
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
        image="mcr.microsoft.com/mssql/server:2017-CU30-ubuntu-18.04",
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
    )


def run_trino(container_name, containers, trino_port):  # pragma: no cover
    containers.run_bg(
        name=container_name,
        image="trinodb/trino",
        volumes={
            TRINO_SETUP_DIR: {"bind": "/trino", "mode": "ro"},
            f"{TRINO_SETUP_DIR}/catalog": {"bind": "/etc/trino/catalog", "mode": "ro"},
        },
        # Choose an arbitrary free port to publish the trino port on
        ports={trino_port: None},
        environment={},
        entrypoint="/trino/entrypoint.sh",
        command="/usr/lib/trino/bin/run-trino",
    )
