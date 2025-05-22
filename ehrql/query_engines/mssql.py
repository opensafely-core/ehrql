import logging

import sqlalchemy
from sqlalchemy.schema import CreateIndex, DropTable
from sqlalchemy.sql.functions import Function as SQLFunction

from ehrql.query_engines.base_sql import BaseSQLQueryEngine, apply_patient_joins
from ehrql.query_engines.mssql_dialect import (
    MSSQLDialect,
    ScalarSelectAggregation,
    SelectStarInto,
)
from ehrql.utils.mssql_log_utils import execute_with_log
from ehrql.utils.sqlalchemy_exec_utils import (
    execute_with_retry_factory,
    fetch_table_in_batches,
)
from ehrql.utils.sqlalchemy_query_utils import GeneratedTable, InsertMany


log = logging.getLogger()


class MSSQLQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = MSSQLDialect

    # Use a CTE as the source for the aggregate query rather than a
    # subquery in order to avoid the "Cannot perform an aggregate function
    # on an expression containing an aggregate or a subquery" error
    def aggregate_series_by_patient(self, source_node, aggregation_func):
        query = self.get_select_query_for_node_domain(source_node)
        from_subquery = query.add_columns(self.get_expr(source_node))
        from_subquery = apply_patient_joins(from_subquery).subquery()
        query = sqlalchemy.select(from_subquery.columns[0])
        aggregation_expr = aggregation_func(from_subquery.columns[1]).label("value")
        return self.apply_sql_aggregation(query, aggregation_expr)

    def calculate_mean(self, sql_expr):
        # Unlike other DBMSs, MSSQL will return an integer as the mean of integers so we
        # have to explicitly cast to float
        if not isinstance(sql_expr.type, sqlalchemy.Float):
            sql_expr = sqlalchemy.cast(sql_expr, sqlalchemy.Float)
        return SQLFunction("AVG", sql_expr, type_=sqlalchemy.Float)

    def date_difference_in_days(self, end, start):
        return SQLFunction(
            "DATEDIFF",
            sqlalchemy.text("day"),
            start,
            end,
            type_=sqlalchemy.Integer,
        )

    def truedivide(self, lhs, rhs):
        rhs_null_if_zero = SQLFunction("NULLIF", rhs, 0.0, type_=sqlalchemy.Float)
        return lhs / rhs_null_if_zero

    def get_date_part(self, date, part):
        assert part in {"YEAR", "MONTH", "DAY"}
        return SQLFunction(part, date, type_=sqlalchemy.Integer)

    def date_add_days(self, date, num_days):
        return SQLFunction(
            "DATEADD",
            sqlalchemy.text("day"),
            num_days,
            date,
            type_=sqlalchemy.Date,
        )

    def date_add_months(self, date, num_months):
        new_date = SQLFunction(
            "DATEADD",
            sqlalchemy.text("month"),
            num_months,
            date,
            type_=sqlalchemy.Date,
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
            type_=sqlalchemy.Date,
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
            type_=sqlalchemy.Date,
        )

    def to_first_of_month(self, date):
        return SQLFunction(
            "DATEFROMPARTS",
            self.get_date_part(date, "YEAR"),
            self.get_date_part(date, "MONTH"),
            1,
            type_=sqlalchemy.Date,
        )

    def reify_query(self, query):
        # The `#` prefix is an MSSQL-ism which automatically makes the tables
        # session-scoped temporary tables
        return temporary_table_from_query(
            table_name=f"#tmp_{self.get_next_id()}",
            query=query,
            index_col="patient_id",
        )

    def create_inline_table(self, columns, rows):
        table_name = f"#inline_data_{self.get_next_id()}"
        table = GeneratedTable(
            table_name,
            sqlalchemy.MetaData(),
            *columns,
        )
        table.setup_queries = [
            sqlalchemy.schema.CreateTable(table),
            InsertMany(table, rows),
            sqlalchemy.schema.CreateIndex(
                sqlalchemy.Index(None, table.c[0], mssql_clustered=True)
            ),
        ]
        return table

    def get_results_queries(self, dataset):
        results_queries = super().get_results_queries(dataset)
        # Write results to temporary tables and select them from there. This allows us
        # to use more efficient/robust mechanisms to retrieve the results.
        select_queries = []
        for n, results_query in enumerate(results_queries, start=1):
            results_table = temporary_table_from_query(
                # The double `##` prefix here makes this a global temporary table, i.e.
                # one accessible to other sessions, hence we need a globally unique
                # name. This allows us to use a separate connection to retrieve results
                # which gives us more robust retries.
                f"##results_{self.global_unique_id}_{n}",
                results_query,
                index_col=0,
            )
            select_query = sqlalchemy.select(results_table)
            # Copy over any annotations on the original query
            select_query = select_query._annotate(results_query._annotations)
            select_queries.append(select_query)
        return select_queries

    def execute_query_no_results(self, connection, query, query_id):
        execute_with_log(connection, query, log.info, query_id=query_id)

    def execute_query_with_results(self, connection, query, query_id):
        # The query type tells us what sort of method we can use for fetching results.
        # We prefer a batched approach using a unique key, but that's not always
        # possible.
        query_type = query._annotations["query_type"]

        # We use a separate connection to retrieve the results. Our intial connection
        # keeps the temporary table "alive" and then this connection can be safely reset
        # and retried if we hit errors during the download (which we often do for
        # reasons we don't yet understand).
        with self.engine.connect() as results_connection:
            # Retry 4 times over the course of 1 minute
            execute_with_retry = execute_with_retry_factory(
                results_connection,
                max_retries=4,
                retry_sleep=4.0,
                backoff_factor=2,
                log=log.info,
            )

            if query_type is self.QueryType.PATIENT_LEVEL:
                yield from self.fetch_results_batched(
                    execute_with_retry,
                    query,
                    key_is_unique=True,
                )
            elif query_type is self.QueryType.EVENT_LEVEL:
                yield from self.fetch_results_batched(
                    execute_with_retry,
                    query,
                    key_is_unique=False,
                )
            elif query_type is self.QueryType.AGGREGATED:
                yield from self.fetch_results_in_one_go(
                    execute_with_retry,
                    query,
                )
            else:
                assert False, f"Unhandled query type: {query_type}"

    def fetch_results_batched(self, execute, query, key_is_unique):
        # We're expecting queries in a very specific form which is "select everything
        # from a single table with a patient_id column"; so we assert that each query
        # has this form and retrieve a reference to the table
        results_table = query.get_final_froms()[0]
        assert str(query) == str(sqlalchemy.select(results_table))
        assert "patient_id" in results_table.columns

        return fetch_table_in_batches(
            execute,
            results_table,
            key_column_index=results_table.columns.keys().index("patient_id"),
            key_is_unique=key_is_unique,
            # This value was copied from the previous cohortextractor. I suspect it
            # has no real scientific basis.
            batch_size=32000,
            log=log.info,
        )

    def fetch_results_in_one_go(self, execute, query):
        results_table = query.get_final_froms()[0]
        log.info(f"Fetching rows from '{results_table}'")
        return execute(query)

    def get_sqlalchemy_execution_options(self):
        # All our queries are either (a) read-only queries against static data, or
        # (b) queries which modify session-scoped temporary tables. This means we
        # can use the DBAPI-level AUTOCOMMIT isolation level which causes all
        # statements to commit immediately.
        return {"isolation_level": "AUTOCOMMIT"}

    def get_aggregate_subquery(self, aggregate_function, columns, return_type):
        return ScalarSelectAggregation.build(
            aggregate_function, columns, type_=return_type
        )


def temporary_table_from_query(table_name, query, index_col=0):
    # Define a table object with the same columns as the query
    table = GeneratedTable.from_query(table_name, query)
    table.setup_queries = [
        # Use the MSSQL `SELECT * INTO ...` construct to create and populate this
        # table
        SelectStarInto(table, query.alias()),
        # Create a clustered index on the specified column which defines the order in
        # which data will be stored on disk. (We use `None` as the index name to let
        # SQLAlchemy generate one for us.)
        CreateIndex(sqlalchemy.Index(None, table.c[index_col], mssql_clustered=True)),
    ]
    table.cleanup_queries = [DropTable(table, if_exists=True)]
    return table
