import sqlalchemy
import structlog
from sqlalchemy.schema import CreateIndex
from sqlalchemy.sql.functions import Function as SQLFunction

from databuilder import sqlalchemy_types
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_engines.mssql_dialect import MSSQLDialect, SelectStarInto
from databuilder.sqlalchemy_utils import (
    GeneratedTable,
    fetch_table_in_batches,
    get_setup_and_cleanup_queries,
)

log = structlog.getLogger()


class MSSQLQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = MSSQLDialect

    # The `#` prefix is an MSSQL-ism which automatically makes the tables session-scoped
    # temporary tables
    intermediate_table_prefix = "#tmp_"

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
        results_table = temporary_table_from_query(
            "#results", results_query, index_col="patient_id"
        )
        return sqlalchemy.select(results_table)

    def get_results(self, variable_definitions):
        results_query = self.get_query(variable_definitions)

        # We're expecting a query in a very specific form which is "select everything
        # from one table"; so we assert that it has this form and retrieve a reference
        # to the table
        results_table = results_query.get_final_froms()[0]
        assert str(results_query) == str(sqlalchemy.select(results_table))

        setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)
        with self.engine.connect() as connection:
            for n, setup_query in enumerate(setup_queries, start=1):
                log.info(f"Running setup query {n:03} / {len(setup_queries):03}")
                connection.execute(setup_query)

            yield from fetch_table_in_batches(
                connection,
                results_table,
                key_column=results_table.c.patient_id,
                # This value was copied from the previous cohortextractor. I suspect it
                # has no real scientific basis.
                batch_size=32000,
                log=log.info,
            )

            assert not cleanup_queries, "Support these once tests exercise them"


def temporary_table_from_query(table_name, query, index_col=0):
    # Define a table object with the same columns as the query
    columns = [
        sqlalchemy.Column(c.name, c.type, key=c.key) for c in query.selected_columns
    ]
    table = GeneratedTable(table_name, sqlalchemy.MetaData(), *columns)
    table.setup_queries = [
        # Use the MSSQL `SELECT * INTO ...` construct to create and populate this
        # table
        SelectStarInto(table, query.alias()),
        # Create a clustered index on the specified column which defines the order in
        # which data will be stored on disk. (We use `None` as the index name to let
        # SQLAlchemy generate one for us.)
        CreateIndex(sqlalchemy.Index(None, table.c[index_col], mssql_clustered=True)),
    ]
    # The "#" prefix ensures this is a session-scoped temporary table so there's no
    # explict cleanup needed
    assert table_name.startswith("#")
    return table
