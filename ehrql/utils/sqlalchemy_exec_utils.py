import time

from sqlalchemy import select
from sqlalchemy.exc import InternalError, OperationalError


def fetch_table_in_batches(
    execute, table, key_column, batch_size=32000, log=lambda *_: None
):
    """
    Returns an iterator over all the rows in a table by querying it in batches

    Args:
        execute: callable which accepts a SQLAlchemy query and returns results (can be
            just a Connection.execute method)
        table: SQLAlchemy TableClause
        key_column: reference to a unique orderable column on `table`, used for
            paging (note that this will need an index on it to avoid terrible
            performance)
        batch_size: how many results to fetch in each batch
        log: callback to receive log messages
    """
    batch_count = 1
    total_rows = 0
    min_key = None

    key_column_index = table.columns.values().index(key_column)

    log(f"Fetching rows from '{table}' in batches of {batch_size}")
    while True:
        query = select(table).order_by(key_column).limit(batch_size)
        if min_key is not None:
            query = query.where(key_column > min_key)

        log(f"Fetching batch {batch_count}")
        results = execute(query)

        row_count = 0
        for row in results:
            row_count += 1
            yield row

        total_rows += row_count
        batch_count += 1

        if row_count < batch_size:
            log(f"Fetch complete, total rows: {total_rows}")
            break
        else:
            min_key = row[key_column_index]


def execute_with_retry_factory(
    execute, max_retries=0, retry_sleep=0, backoff_factor=1, log=lambda *_: None
):
    """
    Wraps a `Connection.execute` method in logic which retries on certain classes of
    error, using an expontential backoff strategy
    """

    def execute_with_retry(*args, **kwargs):
        retries = 0
        next_sleep = retry_sleep

        while True:
            if retries > 0:
                log(f"Retrying query (attempt {retries} / {max_retries})")
            try:
                return execute(*args, **kwargs)
            except (OperationalError, InternalError) as e:
                if retries >= max_retries:
                    raise
                retries += 1
                log(f"{e.__class__.__name__}: {e}")
                log(f"Waiting {next_sleep}s before retrying")
                time.sleep(next_sleep)
                next_sleep *= backoff_factor

    return execute_with_retry


class ReconnectableConnection:
    """
    Context manager which takes an `Engine` and provides a connection-like object which
    supports disconnection and reconnection.

    The `execute_disconnect_on_error()` method acts as `execute()` but if it encounters
    an error it will disconnect before raising them. Subsequent calls to `execute()`
    will automatically attempt to reconnect.
    """

    _connection = None

    def __init__(self, engine, **connect_kwargs):
        self.engine = engine
        self.connect_kwargs = connect_kwargs

    def _get_connection(self):
        if self._connection is None:
            self._connection = self.engine.connect(**self.connect_kwargs)
        return self._connection

    def __enter__(self):
        self._get_connection()
        return self

    def __exit__(self, *args):
        if self._connection is not None:
            self._connection.close()

    def execute(self, *args, **kwargs):
        return self._get_connection().execute(*args, **kwargs)

    def execute_disconnect_on_error(self, *args, **kwargs):
        try:
            return self.execute(*args, **kwargs)
        except Exception:
            self.disconnect()
            raise

    def disconnect(self):
        if self._connection is None:
            return
        # Remove the connection from the pool so that calling `close()` will actually
        # close it rather than just returning it to the pool
        self._connection.detach()
        self._connection.close()
        self._connection = None
