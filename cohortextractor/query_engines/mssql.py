import contextlib
import datetime

import sqlalchemy
import sqlalchemy.dialects.mssql
import sqlalchemy.schema
import sqlalchemy.types

from .base_sql import BaseSQLQueryEngine
from .mssql_lib import fetch_results_in_batches, write_query_to_table


# MS-SQL can misinterpret ISO dates, depending on its localisation settings so
# we need to use particular date formats which we know will be consistently
# interpreted. We do this by defining custom SQLAlchemy types. See:
# https://github.com/opensafely-core/cohort-extractor-v2/issues/92
# http://msdn.microsoft.com/en-us/library/ms180878.aspx
# https://stackoverflow.com/a/25548626/559140
class _MSSQLDateTimeBase:
    text_type = sqlalchemy.types.Text()

    def process_bind_param(self, value, dialect):
        """
        Convert a Python value to a form suitable for passing as a parameter to
        the database connector
        """
        # Note that None values will be cooerced to IS/IS NOT expressions by
        # sqlalchemy.type.TypeDecorator so we don't need to deal with them here
        # We accept ISO formated strings as well
        if isinstance(value, str):
            value = self.date_type.fromisoformat(value)
        if not isinstance(value, self.date_type):
            raise TypeError(f"Expected {self.date_type} or str got: {value!r}")
        return value.strftime(self.format_str)

    def process_literal_param(self, value, dialect):
        """
        Convert a Python value into an escaped string suitable for
        interpolating directly into an SQL string
        """
        # Use the above method to convert to a string first
        value = self.process_bind_param(value, dialect)
        # Use the Text literal processor to quote and escape that string
        literal_processor = self.text_type.literal_processor(dialect)
        return literal_processor(value)


class MSSQLDate(_MSSQLDateTimeBase, sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.Date
    cache_ok = True
    date_type = datetime.date
    # See https://stackoverflow.com/a/25548626/559140
    format_str = "%Y%m%d"


class MSSQLDateTime(_MSSQLDateTimeBase, sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.DateTime
    cache_ok = True
    date_type = datetime.datetime
    # See https://stackoverflow.com/a/25548626/559140
    format_str = "%Y-%m-%dT%H:%M:%S"


class MssqlQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = sqlalchemy.dialects.mssql

    custom_types = {
        "date": MSSQLDate,
        "datetime": MSSQLDateTime,
    }

    # MSSQL limit on number of rows that can inserted using a single,
    # mutli-valued INSERT statement. See:
    # https://docs.microsoft.com/en-us/sql/t-sql/queries/table-value-constructor-transact-sql?view=sql-server-ver15#limitations-and-restrictions
    max_rows_per_insert = 999

    def write_query_to_table(self, table, query):
        """
        Returns a new query which, when executed, writes the results of `query`
        into `table`
        """
        return write_query_to_table(table, query)

    def get_temp_table_name(self, table_name):
        """
        Return a table name based on `table_name` but suitable for use as a
        temporary table.

        It's the caller's responsibility to ensure `table_name` is unique
        within this session; it's this function's responsibility to ensure it
        doesn't clash with any concurrent extracts
        """
        # The `#` prefix makes this a session-scoped temporary table which
        # automatically gives us the isolation we need
        return f"#{table_name}"

    @contextlib.contextmanager
    def execute_query(self):
        """Execute a query against an MSSQL backend"""
        if self.backend.temporary_database:
            # If we've got access to a temporary database then we use this
            # function to manage storing our results in there and downloading
            # in batches. This gives us the illusion of having a robust
            # connection to the database, whereas in practice in frequently
            # errors out when attempting to download large sets of results.
            queries = self.get_queries()
            with fetch_results_in_batches(
                engine=self.engine,
                queries=queries,
                # The double dot syntax allows us to reference tables in another database
                temp_table_prefix=f"{self.backend.temporary_database}..TempExtract",
                # This value was copied from the previous cohortextractor. I
                # suspect it has no real scientific basis.
                batch_size=32000,
                max_retries=2,
                sleep=0.5,
                reconnect_on_error=True,
            ) as results:
                yield results
        else:
            # Otherwise we just execute the queries and download the results in
            # the normal manner
            with super().execute_query() as results:
                yield results
