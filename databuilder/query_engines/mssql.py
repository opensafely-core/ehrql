import sqlalchemy

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
        func = sqlalchemy.func
        get_part = {"YEAR": func.year, "MONTH": func.month, "DAY": func.day}[part]
        # Tell SQLAlchemy that the result is an int without doing any CASTing in the SQL
        return sqlalchemy.type_coerce(get_part(date), sqlalchemy_types.Integer())

    def date_add_days(self, date, num_days):
        new_date = sqlalchemy.func.dateadd(sqlalchemy.text("day"), num_days, date)
        # Tell SQLAlchemy that the result is a date without doing any CASTing in the SQL
        return sqlalchemy.type_coerce(new_date, sqlalchemy_types.Date())

    def reify_query(self, query):
        # Define a table object with the same columns as the query
        table_name = self.next_intermediate_table_name()
        columns = [
            sqlalchemy.Column(c.name, c.type, key=c.key) for c in query.selected_columns
        ]
        table = GeneratedTable(table_name, sqlalchemy.MetaData(), *columns)
        # Use the MSSQL `SELECT * INTO ...` construct to create and populate this table
        table.setup_queries = [SelectStarInto(table, query.alias())]
        # The "#" in `intermediate_table_prefix` ensures this is a session-scoped
        # temporary table so there's no explict cleanup needed
        return table
