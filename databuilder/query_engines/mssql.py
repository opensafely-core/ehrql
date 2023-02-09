import datetime
import secrets

import sqlalchemy
import structlog
from sqlalchemy.schema import CreateIndex, DropTable
from sqlalchemy.sql.functions import Function as SQLFunction

from databuilder import sqlalchemy_types
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_engines.mssql_dialect import MSSQLDialect, SelectStarInto
from databuilder.utils.sqlalchemy_exec_utils import (
    ReconnectableConnection,
    execute_with_retry_factory,
    fetch_table_in_batches,
)
from databuilder.utils.sqlalchemy_query_utils import (
    GeneratedTable,
    expr_has_type,
    get_setup_and_cleanup_queries,
)

log = structlog.getLogger()


class MSSQLQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = MSSQLDialect

    # The `#` prefix is an MSSQL-ism which automatically makes the tables session-scoped
    # temporary tables
    intermediate_table_prefix = "#tmp_"

    def calculate_mean(self, sql_expr):
        # Unlike other DBMSs, MSSQL will return an integer as the mean of integers so we
        # have to explicitly cast to float
        if not expr_has_type(sql_expr, sqlalchemy_types.Float):
            sql_expr = sqlalchemy.cast(sql_expr, sqlalchemy_types.Float)
        return sqlalchemy.func.avg(sql_expr, type_=sqlalchemy_types.Float)

    def date_difference_in_days(self, end, start):
        return SQLFunction(
            "DATEDIFF",
            sqlalchemy.text("day"),
            start,
            end,
            type_=sqlalchemy_types.Integer,
        )

    def get_date_part(self, date, part):
        assert part in {"YEAR", "MONTH", "DAY"}
        return SQLFunction(part, date, type_=sqlalchemy_types.Integer)

    def date_add_days(self, date, num_days):
        return SQLFunction(
            "DATEADD",
            sqlalchemy.text("day"),
            num_days,
            date,
            type_=sqlalchemy_types.Date,
        )

    def date_add_months(self, date, num_months):
        new_date = SQLFunction(
            "DATEADD",
            sqlalchemy.text("month"),
            num_months,
            date,
            type_=sqlalchemy_types.Date,
        )
        # In cases of day-of-month overflow, MSSQL clips to the end of the month rather
        # than rolling over to the first of the next month as want it to, so we detect
        # when it's done that and correct for it here. For more detail see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_months
        correction = sqlalchemy.case(
            (self.get_date_part(new_date, "DAY") < self.get_date_part(date, "DAY"), 1),
            else_=0,
        )
        return self.date_add_days(new_date, correction)

    def date_add_years(self, date, num_years):
        # We can't just use `DATEADD(year, ...)` here due to MSSQL's insistence on
        # rounding 29 Feb down rather than up on non-leap years. For more detail see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_years
        #
        # First, do the year shifting arithmetic on the start of the month where there's
        # no leap year shenanigans to content with.
        start_of_month = SQLFunction(
            "DATEFROMPARTS",
            self.get_date_part(date, "YEAR") + num_years,
            self.get_date_part(date, "MONTH"),
            1,
            type_=sqlalchemy_types.Date,
        )
        # Then add on the number of days we're offset from the start of the month which
        # has the effect of rolling 29 Feb over to 1 Mar as we want
        return self.date_add_days(start_of_month, self.get_date_part(date, "DAY") - 1)

    def to_first_of_year(self, date):
        return SQLFunction(
            "DATEFROMPARTS",
            self.get_date_part(date, "YEAR"),
            1,
            1,
            type_=sqlalchemy_types.Date,
        )

    def to_first_of_month(self, date):
        return SQLFunction(
            "DATEFROMPARTS",
            self.get_date_part(date, "YEAR"),
            self.get_date_part(date, "MONTH"),
            1,
            type_=sqlalchemy_types.Date,
        )

    def reify_query(self, query):
        return temporary_table_from_query(
            self.next_intermediate_table_name(), query, index_col="patient_id"
        )

    def get_query(self, variable_definitions):
        results_query = super().get_query(variable_definitions)
        # Write results to a temporary table and select them from there. This allows us
        # to use more efficient/robust mechanisms to retrieve the results.
        table_name, schema = self.get_results_table_name_and_schema(
            self.config.get("TEMP_DATABASE_NAME")
        )
        results_table = temporary_table_from_query(
            table_name, results_query, index_col="patient_id", schema=schema
        )
        return sqlalchemy.select(results_table)

    def get_results_table_name_and_schema(self, temp_database_name):
        # If we have a temporary database we can write results there which enables
        # us to continue retrieving results after an interrupted connection
        if temp_database_name:
            # As the table is not session-scoped it needs a unique name
            timestamp = datetime.datetime.utcnow()
            token = secrets.token_hex(6)
            table_name = f"results_{timestamp:%Y%m%d_%H%M}_{token}"
            # The `schema` variable below is actually a multi-part identifier of the
            # form `<database-name>.<schema>`. We don't really care about the schema
            # here, we just want to use whatever is the default schema for the database.
            # MSSQL allows you to do this by specifying "." as the schema name. However
            # I can't find a way of supplying this without SQLAlchemy's quoting
            # algorithm either mangling it or blowing up. We could work around this by
            # attaching our own Identifier Preparer to our MSSQL dialect, but that
            # sounds a lot like hard work. So we use the default value for the default
            # schema, which is "dbo" (Database Owner), on the assumption that this will
            # generally work and we can revisit if we have to. Relevant URLs are:
            # https://docs.sqlalchemy.org/en/14/dialects/mssql.html#multipart-schema-names
            # https://github.com/sqlalchemy/sqlalchemy/blob/8c07c68c/lib/sqlalchemy/dialects/mssql/base.py#L2799
            schema = f"{temp_database_name}.dbo"
        else:
            # Otherwise we use a session-scoped temporary table which requires a
            # continuous connnection
            table_name = "#results"
            schema = None
        return table_name, schema

    def get_results(self, variable_definitions):
        results_query = self.get_query(variable_definitions)

        # We're expecting a query in a very specific form which is "select everything
        # from one table"; so we assert that it has this form and retrieve a reference
        # to the table
        results_table = results_query.get_final_froms()[0]
        assert str(results_query) == str(sqlalchemy.select(results_table))

        setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)

        # Because we may be disconnecting and reconnecting to the database part way
        # through downloading results we need to make sure that the temporary tables we
        # create, and the commands which delete them, get committed. There's no need for
        # careful transaction management here: we just want them committed immediately.
        autocommit_engine = self.engine.execution_options(isolation_level="AUTOCOMMIT")

        with ReconnectableConnection(autocommit_engine) as connection:
            for n, setup_query in enumerate(setup_queries, start=1):
                log.info(f"Running setup query {n:03} / {len(setup_queries):03}")
                connection.execute(setup_query)

            # Re-establishing the database connection after an error allows us to
            # recover from a wider range of failure modes. But we can only do this if
            # the table we're reading from persists across connections.
            if results_table.is_persistent:
                conn_execute = connection.execute_disconnect_on_error
            else:
                conn_execute = connection.execute

            # Retry 6 times over ~90m
            execute_with_retry = execute_with_retry_factory(
                conn_execute,
                max_retries=6,
                retry_sleep=4.0,
                backoff_factor=4,
                log=log.info,
            )

            yield from fetch_table_in_batches(
                execute_with_retry,
                results_table,
                key_column=results_table.c.patient_id,
                # This value was copied from the previous cohortextractor. I suspect it
                # has no real scientific basis.
                batch_size=32000,
                log=log.info,
            )

            for n, cleanup_query in enumerate(cleanup_queries, start=1):
                log.info(f"Running cleanup query {n:03} / {len(cleanup_queries):03}")
                connection.execute(cleanup_query)


def temporary_table_from_query(table_name, query, index_col=0, schema=None):
    # Define a table object with the same columns as the query
    columns = [
        sqlalchemy.Column(c.name, c.type, key=c.key) for c in query.selected_columns
    ]
    table = GeneratedTable(table_name, sqlalchemy.MetaData(), *columns, schema=schema)
    table.setup_queries = [
        # Use the MSSQL `SELECT * INTO ...` construct to create and populate this
        # table
        SelectStarInto(table, query.alias()),
        # Create a clustered index on the specified column which defines the order in
        # which data will be stored on disk. (We use `None` as the index name to let
        # SQLAlchemy generate one for us.)
        CreateIndex(sqlalchemy.Index(None, table.c[index_col], mssql_clustered=True)),
    ]
    # The "#" prefix indicates a session-scoped temporary table which doesn't need
    # explict cleanup
    if table_name.startswith("#"):
        table.is_persistent = False
        table.cleanup_queries = []
    else:
        table.is_persistent = True
        table.cleanup_queries = [DropTable(table)]
    return table
