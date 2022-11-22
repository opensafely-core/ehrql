import sqlalchemy
from sqlalchemy.sql.functions import Function as SQLFunction

from databuilder import sqlalchemy_types
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.query_engines.spark_dialect import CreateTemporaryViewAs, SparkDialect
from databuilder.utils.sqlalchemy_query_utils import GeneratedTable


class SparkQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = SparkDialect

    def date_difference_in_days(self, end, start):
        return SQLFunction("DATEDIFF", end, start, type_=sqlalchemy_types.Integer)

    def get_date_part(self, date, part):
        assert part in {"YEAR", "MONTH", "DAY"}
        return SQLFunction(part, date, type_=sqlalchemy_types.Integer)

    def date_add_days(self, date, num_days):
        return SQLFunction("DATE_ADD", date, num_days, type_=sqlalchemy_types.Date)

    def date_add_months(self, date, num_months):
        new_date = SQLFunction(
            "ADD_MONTHS", date, num_months, type_=sqlalchemy_types.Date
        )
        # In cases of day-of-month overflow, Spark clips to the end of the month rather
        # than rolling over to the first of the next month as want it to, so we detect
        # when it's done that and correct for it here. For more detail see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_months
        correction = sqlalchemy.case(
            (self.get_date_part(new_date, "DAY") < self.get_date_part(date, "DAY"), 1),
            else_=0,
        )
        return self.date_add_days(new_date, correction)

    def date_add_years(self, date, num_years):
        # We can't just use `ADD_MONTHS` directly here due to Spark's insistence on
        # rounding 29 Feb down rather than up on non-leap years. For more detail see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_years
        #
        # Instead we truncate the date to the fist of the month, shift the year, and
        # then add the relevant number of days back on which has the effect of rolling
        # 29 Feb over to 1 Mar as we want.
        start_of_month = self.to_first_of_month(date)
        # Spark doesn't have a native ADD_YEARS function so we have to use months
        offset_result = SQLFunction("ADD_MONTHS", start_of_month, num_years * 12)
        return self.date_add_days(offset_result, self.get_date_part(date, "DAY") - 1)

    def to_first_of_year(self, date):
        return SQLFunction("TRUNC", date, "year", type_=sqlalchemy_types.Date)

    def to_first_of_month(self, date):
        return SQLFunction("TRUNC", date, "month", type_=sqlalchemy_types.Date)

    def reify_query(self, query):
        # Define a table object with the same columns as the query
        table_name = self.next_intermediate_table_name()
        columns = [
            sqlalchemy.Column(c.name, c.type, key=c.key) for c in query.selected_columns
        ]
        table = GeneratedTable(table_name, sqlalchemy.MetaData(), *columns)
        # Create a temporary (session-scoped) view from the query
        table.setup_queries = [CreateTemporaryViewAs(table, query)]
        return table
