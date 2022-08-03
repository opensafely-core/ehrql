import sqlalchemy
from sqlalchemy.schema import CreateIndex
from sqlalchemy.sql.functions import Function as SQLFunction

from databuilder import sqlalchemy_types
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_engines.mssql_dialect import MSSQLDialect, SelectStarInto
from databuilder.sqlalchemy_utils import GeneratedTable


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
