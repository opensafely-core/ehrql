import sqlalchemy
from sqlalchemy.sql.functions import Function as SQLFunction

from databuilder import sqlalchemy_types
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_engines.sqlite_dialect import SQLiteDialect


class SQLiteQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = SQLiteDialect

    def date_difference_in_days(self, end, start):
        start_day = SQLFunction("JULIANDAY", start)
        end_day = SQLFunction("JULIANDAY", end)
        return sqlalchemy.cast(end_day - start_day, sqlalchemy_types.Integer)

    def get_date_part(self, date, part):
        format_str = {"YEAR": "%Y", "MONTH": "%m", "DAY": "%d"}[part]
        part_as_str = SQLFunction("STRFTIME", format_str, date)
        return sqlalchemy.cast(part_as_str, sqlalchemy_types.Integer)

    def date_add_days(self, date, num_days):
        return self.date_add("days", date, num_days)

    def date_add_years(self, date, num_years):
        return self.date_add("years", date, num_years)

    def date_add(self, units, date, value):
        value_str = sqlalchemy.cast(value, sqlalchemy_types.String)
        modifier = value_str.concat(f" {units}")
        return SQLFunction("DATE", date, modifier, type_=sqlalchemy_types.Date)

    def to_first_of_year(self, date):
        return SQLFunction("DATE", date, "start of year", type_=sqlalchemy_types.Date)

    def to_first_of_month(self, date):
        return SQLFunction("DATE", date, "start of month", type_=sqlalchemy_types.Date)
