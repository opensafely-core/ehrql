import contextlib

import sqlalchemy
import sqlalchemy.sql.ddl
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

    # The `#` prefix is an MSSQL-ism which automatically makes the tables session-scoped
    # temporary tables
    temp_table_prefix = "#"

    def query_to_create_temp_table_from_select_query(self, table, select_query):
        """
        Return a query to create `table` and populate it with the results of
        `select_query`
        """
        return write_query_to_table(table, select_query)

    def temp_table_needs_dropping(self, create_table_query):
        """
        We're expecting to only ever create tables with the special "#" prefix which
        marks them as session-scoped temporary tables which don't require cleanup. This
        method just asserts that this expectation is met.
        """
        if isinstance(create_table_query, sqlalchemy.sql.Select):
            into_clause = create_table_query.selected_columns[0].name
            assert into_clause.startswith("* INTO #")
        elif isinstance(create_table_query, sqlalchemy.sql.ddl.CreateTable):
            table_name = create_table_query.element.name
            assert table_name.startswith("#")
        else:
            assert False

        return False

    @contextlib.contextmanager
    def execute_query(self, column_definitions):
        """Execute a query against an MSSQL backend"""
        if self.backend.temporary_database:
            # If we've got access to a temporary database then we use this
            # function to manage storing our results in there and downloading
            # in batches. This gives us the illusion of having a robust
            # connection to the database, whereas in practice in frequently
            # errors out when attempting to download large sets of results.
            setup_queries, results_query, cleanup_queries = self.get_queries(
                column_definitions
            )
            # We're not expecting to have any cleanup to do here because we should be
            # using session-scoped temporary tables
            assert not cleanup_queries
            with fetch_results_in_batches(
                engine=self.engine,
                queries=setup_queries + [results_query],
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
            with super().execute_query(column_definitions) as results:
                yield results

    def _convert_date_diff_to_days(
        self, start, end
    ):  # pragma: no cover (re-implement when the QL is in)
        """
        Calculate difference in days
        """
        return sqlalchemy.func.datediff(sqlalchemy.text("day"), start, end)

    def date_add(
        self, start_date, number_of_days
    ):  # pragma: no cover (re-implement when the QL is in)
        """
        Add a number of days to a date, using the `dateadd` function
        """
        start_date = type_coerce(start_date, sqlalchemy_types.Date())
        return type_coerce(
            sqlalchemy.func.dateadd(sqlalchemy.text("day"), number_of_days, start_date),
            sqlalchemy_types.Date(),
        )

    def date_subtract(
        self, start_date, number_of_days
    ):  # pragma: no cover (re-implement when the QL is in)
        """
        Subtract a number of days from a date, using the `dateadd` function
        """
        start_date = type_coerce(start_date, sqlalchemy_types.Date())
        return type_coerce(
            sqlalchemy.func.dateadd(
                sqlalchemy.text("day"), number_of_days * -1, start_date
            ),
            sqlalchemy_types.Date(),
        )

    def round_to_first_of_month(
        self, date
    ):  # pragma: no cover (re-implement when the QL is in)
        date = type_coerce(date, sqlalchemy_types.Date())
        first_of_month = sqlalchemy.func.datefromparts(
            sqlalchemy.func.year(date), sqlalchemy.func.month(date), 1
        )
        return type_coerce(first_of_month, sqlalchemy_types.Date())

    def round_to_first_of_year(
        self, date
    ):  # pragma: no cover (re-implement when the QL is in)
        date = type_coerce(date, sqlalchemy_types.Date())
        first_of_year = sqlalchemy.func.datefromparts(sqlalchemy.func.year(date), 1, 1)
        return type_coerce(first_of_year, sqlalchemy_types.Date())
