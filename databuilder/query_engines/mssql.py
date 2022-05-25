import sqlalchemy

from databuilder import sqlalchemy_types
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_engines.mssql_dialect import MSSQLDialect


class MSSQLQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = MSSQLDialect

    def get_date_part(self, date, part):
        func = sqlalchemy.func
        get_part = {"YEAR": func.year, "MONTH": func.month, "DAY": func.day}[part]
        return sqlalchemy.type_coerce(get_part(date), sqlalchemy_types.Integer())

    def date_add_days(self, date, num_days):
        new_date = sqlalchemy.func.dateadd(sqlalchemy.text("day"), num_days, date)
        # Tell SQLAlchemy that the result is a date without doing any CASTing in the SQL
        return sqlalchemy.type_coerce(new_date, sqlalchemy_types.Date())
