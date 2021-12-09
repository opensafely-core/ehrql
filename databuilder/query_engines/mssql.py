import contextlib

import sqlalchemy
from sqlalchemy.sql.expression import type_coerce

from .. import sqlalchemy_types
from .base_sql import BaseSQLQueryEngine
from .mssql_dialect import MSSQLDialect
from .mssql_lib import fetch_results_in_batches, write_query_to_table


class MssqlQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = MSSQLDialect

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

    def round_to_first_of_month(self, date):
        date = type_coerce(date, sqlalchemy_types.Date())

        first_of_month = sqlalchemy.func.datefromparts(
            sqlalchemy.func.year(date),
            sqlalchemy.func.month(date),
            1,
        )

        return type_coerce(first_of_month, sqlalchemy_types.Date())

    def round_to_first_of_year(self, date):
        date = type_coerce(date, sqlalchemy_types.Date())

        first_of_year = sqlalchemy.func.datefromparts(
            sqlalchemy.func.year(date),
            1,
            1,
        )

        return type_coerce(first_of_year, sqlalchemy_types.Date())
