from unittest import mock

import pytest
import sqlalchemy

from cohortextractor2.query_engines.mssql_lib import (
    ReconnectableConnection,
    fetch_results_in_batches,
)


@pytest.mark.integration
def test_fetch_results_in_batches_happy_path(database):
    table = sqlalchemy.table("test_table")
    test_data = _make_test_data(rows=12)

    engine = database.engine()
    with engine.connect() as conn:
        _populate_table(conn, table, test_data)

    query = sqlalchemy.select("*").select_from(table)
    with fetch_results_in_batches(
        engine,
        [query],
        temp_table_prefix="#temp",
        batch_size=5,
        max_retries=0,
    ) as results:
        assert _as_dicts(results) == test_data


@pytest.mark.integration
def test_fetch_results_in_batches_with_retry(database):
    table = sqlalchemy.table("test_table")
    test_data = _make_test_data(rows=12)

    engine = database.engine()
    with engine.connect() as conn:
        _populate_table(conn, table, test_data)

    query = sqlalchemy.select("*").select_from(table)
    with fetch_results_in_batches(
        engine,
        [query],
        # Use a session-scoped temporary table to write results to
        temp_table_prefix="#temp",
        batch_size=5,
        max_retries=1,
        sleep=0.001,
    ) as results:
        with _flaky_connection(fail_on_call_numbers=[1, 3]) as execute:
            assert _as_dicts(results) == test_data
            # 3 to retrieve results + 2 retries
            assert execute.call_count == 5


@pytest.mark.integration
def test_fetch_results_in_batches_with_reconnect_and_retry(database):
    table = sqlalchemy.table("test_table")
    test_data = _make_test_data(rows=12)

    engine = database.engine()
    with engine.connect() as conn:
        _populate_table(conn, table, test_data)

    query = sqlalchemy.select("*").select_from(table)
    with fetch_results_in_batches(
        engine,
        [query],
        # We have to use a persistent table to write results to because we are
        # going to close and reopen the db connection
        temp_table_prefix="temp",
        batch_size=5,
        max_retries=2,
        sleep=0.001,
        reconnect_on_error=True,
    ) as results:
        with _flaky_connection(fail_on_call_numbers=[1, 3]) as execute:
            assert _as_dicts(results) == test_data
            # 3 to retrieve results + 2 retries
            assert execute.call_count == 5


@pytest.mark.integration
def test_fetch_results_in_batches_caches_results(database, temp_tables):
    table = sqlalchemy.table("test_table")
    test_data = _make_test_data(rows=12)

    engine = database.engine()
    with engine.connect() as conn:
        _populate_table(conn, table, test_data)

    query = sqlalchemy.select("*").select_from(table)

    with pytest.raises(sqlalchemy.exc.OperationalError):
        with fetch_results_in_batches(
            engine,
            [query],
            # Write to a persistent table in the "temp_tables" database so we
            # can try to pick up results even after erroring
            temp_table_prefix=temp_tables.prefix,
            max_retries=1,
            sleep=0.001,
        ) as results:
            # Trigger multiple sequential errors to exhaust the retry limit
            with _flaky_connection(fail_on_call_numbers=[1, 2]):
                list(results)

    # Assert we've got one new temporary table
    assert len(temp_tables.list_all()) == 1

    # Now drop the test table to prove that we're using the cached results and
    # not re-running the query
    with engine.connect() as conn:
        conn.execute(sqlalchemy.schema.DropTable(table))

    # Re-run the fetch to pick up the cached results
    with fetch_results_in_batches(
        engine,
        [query],
        temp_table_prefix=temp_tables.prefix,
    ) as results:
        # Assert the results are as expected
        _as_dicts(results) == results

    # Assert that the temporary table has been removed
    assert len(temp_tables.list_all()) == 0


def _flaky_connection(fail_on_call_numbers):
    """
    Patches `ReconnectableConnection.execute` to fail intermittently and
    otherwise to return as normal. Accepts a list of integers which are the
    (1-based) call numbers which should fail.
    """
    original_execute = ReconnectableConnection.execute
    call_counter = 0

    def flaky_execute(self, *args, **kwargs):
        result = original_execute(self, *args, **kwargs)
        nonlocal call_counter
        call_counter += 1
        if call_counter in fail_on_call_numbers:
            raise sqlalchemy.exc.OperationalError(None, None, None)
        return result

    return mock.patch.object(
        ReconnectableConnection,
        "execute",
        side_effect=flaky_execute,
        autospec=True,
    )


def _make_test_data(rows):
    return [{"patient_id": i, "foo": f"foo{i}"} for i in range(1, rows + 1)]


def _populate_table(conn, table, items):
    columns = [
        sqlalchemy.Column(
            name,
            type_=sqlalchemy.Integer if isinstance(value, int) else sqlalchemy.String,
        )
        for (name, value) in items[0].items()
    ]
    table_def = sqlalchemy.Table(table.name, sqlalchemy.MetaData(), *columns)
    conn.execute(sqlalchemy.schema.DropTable(table_def, if_exists=True))
    conn.execute(sqlalchemy.schema.CreateTable(table_def))
    for item in items:
        conn.execute(table_def.insert().values(**item))
    conn.commit()


def _as_dicts(results):
    return [dict(row) for row in results]


@pytest.fixture
def temp_tables(database):
    temp_tables = TempTables(
        engine=database.engine(), database="temp_tables", prefix="temp_"
    )
    temp_tables.drop_all()
    try:
        yield temp_tables
    finally:
        temp_tables.drop_all()  # pragma: no cover


class TempTables:
    """
    Convenience wrapper around temporary tables stored in a separate database
    """

    def __init__(self, engine, database, prefix):
        self.engine = engine
        self.database = database
        self._prefix = prefix

    @property
    def prefix(self):
        return f"{self.database}..{self._prefix}"

    def list_all(self):
        query = sqlalchemy.text(
            f"""
            SELECT table_name FROM {self.database}.information_schema.tables
            WHERE table_type = 'BASE TABLE'
            """
        )
        with self.engine.connect() as conn:
            return sorted(
                row[0] for row in conn.execute(query) if row[0].startswith(self._prefix)
            )

    def drop_all(self):  # pragma: no cover
        tables = self.list_all()
        with self.engine.connect() as conn:
            for table in tables:
                conn.execute(sqlalchemy.text(f"DROP TABLE {self.database}..{table}"))
            conn.commit()
