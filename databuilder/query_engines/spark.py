import sqlalchemy

from databuilder import sqlalchemy_types
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_engines.spark_dialect import SparkDialect


class SparkQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = SparkDialect

    def get_date_part(self, date, part):
        func = sqlalchemy.func
        get_part = {"YEAR": func.year, "MONTH": func.month, "DAY": func.day}[part]
        # Tell SQLAlchemy that the result is an int without doing any CASTing in the SQL
        return sqlalchemy.type_coerce(get_part(date), sqlalchemy_types.Integer())

    def date_add_days(self, date, num_days):
        new_date = sqlalchemy.func.date_add(date, num_days)
        # Tell SQLAlchemy that the result is a date without doing any CASTing in the SQL
        return sqlalchemy.type_coerce(new_date, sqlalchemy_types.Date())
