import sqlalchemy
import structlog
from sqlalchemy.sql.functions import Function as SQLFunction

from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.query_engines.trino_dialect import TrinoDialect


log = structlog.getLogger()


class TrinoQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = TrinoDialect

    def get_date_part(self, date, part):
        assert part in {"YEAR", "MONTH", "DAY"}
        return SQLFunction(part, date, type_=sqlalchemy.Integer)

    def to_first_of_year(self, date):
        return SQLFunction("DATE_TRUNC", "year", date, type_=sqlalchemy.Date)

    def to_first_of_month(self, date):
        return SQLFunction("DATE_TRUNC", "month", date, type_=sqlalchemy.Date)

    def date_add_days(self, date, num_days):
        return SQLFunction(
            "DATE_ADD",
            "day",
            num_days,
            date,
            type_=sqlalchemy.Date,
        )

    def date_add_months(self, date, num_months):
        new_date = SQLFunction(
            "DATE_ADD",
            "month",
            num_months,
            date,
            type_=sqlalchemy.Date,
        )
        # In cases of day-of-month overflow, Trino clips to the end of the month rather
        # than rolling over to the first of the next month as want it to, so we detect
        # when it's done that and correct for it here. For more detail see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_months
        correction = sqlalchemy.case(
            (self.get_date_part(new_date, "DAY") < self.get_date_part(date, "DAY"), 1),
            else_=0,
        )
        return self.date_add_days(new_date, correction)

    def date_add_years(self, date, num_years):
        # We can't just use `DATEADD(year, ...)` here due to Trino's insistence on
        # rounding 29 Feb down rather than up on non-leap years. For more detail see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_years
        #
        # First, do the year shifting arithmetic on the start of the month where there's
        # no leap year shenanigans to content with.
        start_of_month = SQLFunction(
            "DATE_ADD",
            "year",
            num_years,
            self.to_first_of_month(date),
            type_=sqlalchemy.Date,
        )

        # Then add on the number of days we're offset from the start of the month which
        # has the effect of rolling 29 Feb over to 1 Mar as we want
        return self.date_add_days(start_of_month, self.get_date_part(date, "DAY") - 1)

    def date_difference_in_days(self, end, start):
        return SQLFunction(
            "DATE_DIFF",
            "day",
            start,
            end,
            type_=sqlalchemy.Integer,
        )
