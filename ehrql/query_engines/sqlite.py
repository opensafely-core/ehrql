import sqlalchemy
from sqlalchemy.sql.functions import Function as SQLFunction

from ehrql.query_engines.base_sql import BaseSQLQueryEngine, get_cyclic_coalescence
from ehrql.query_engines.sqlite_dialect import SQLiteDialect


class SQLiteQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = SQLiteDialect

    def date_difference_in_days(self, end, start):
        start_day = SQLFunction("JULIANDAY", start)
        end_day = SQLFunction("JULIANDAY", end)
        return sqlalchemy.cast(end_day - start_day, sqlalchemy.Integer)

    def get_date_part(self, date, part):
        format_str = {"YEAR": "%Y", "MONTH": "%m", "DAY": "%d"}[part]
        part_as_str = SQLFunction("STRFTIME", format_str, date)
        return sqlalchemy.cast(part_as_str, sqlalchemy.Integer)

    def date_add_days(self, date, num_days):
        return self.date_add("days", date, num_days)

    def date_add_months(self, date, num_months):
        new_date = self.date_add("months", date, num_months)
        # In cases of day-of-month overflow, SQLite *usually* rolls over to the first of
        # the next month as want it to.
        # It does this by performing a normalisation when a date arithmetic operation results
        # in a date with an invalid number of days (e.g. 30 Feb 2000); namely it
        # rolls over to the next month by incrementing the month and subtracting
        # the number of days in the month. For all months except February, the invalid day is only
        # ever at most 1 day off (i.e. the 31st, for a month with only 30 days), and so this
        # normalisation results in a rollover to the first of the next month. However for February,
        # the invalid day can be 1 to 3 days off, which means date rollovers can result in the 1st,
        # 2nd or 3rd March.
        #
        # The SQLite docs (https://sqlite.org/lang_datefunc.html) state:
        # "Note that "±NNN months" works by rendering the original date into the YYYY-MM-DD
        # format, adding the ±NNN to the MM month value, then normalizing the result. Thus,
        # for example, the date 2001-03-31 modified by '+1 month' initially yields 2001-04-31,
        # but April only has 30 days so the date is normalized to 2001-05-01"
        #
        # i.e. 2001-03-31 +1 month results in 2001-04-31, but as the number of days is invalid,
        # SQLite rolls over to the next month by incrementing the month by 1, and subtracting
        # the number of days in April (30) from the days, resulting in 2001-05-01
        #
        # In the case of February, a calculation that results in a date with an invalid number of
        # days follows the same normalisation method:
        # 2000-02-30: increment month by 1, subtract 29 (leap year) days -> 2000-03-01
        # 2001-02-30: increment month by 1, subtract 28 days -> 2000-03-02
        # 2000-02-31: increment month by 1, subtract 29 (leap year) days -> 2000-03-02
        # 2001-02-31: increment month by 1, subtract 28 days -> 2000-03-03
        #
        # We detect when it's done that and correct for it here, ensuring that when a date rolls over
        # to the next month, the date returned is always the first of that month. For more detail see:
        # tests/spec/date_series/ops/test_date_series_ops.py::test_add_months
        new_date_day = self.get_date_part(new_date, "DAY")
        correction = sqlalchemy.case(
            (
                self.get_date_part(new_date, "DAY") < self.get_date_part(date, "DAY"),
                1 - new_date_day,
            ),
            else_=0,
        )
        return self.date_add_days(new_date, correction)

    def date_add_years(self, date, num_years):
        return self.date_add("years", date, num_years)

    def date_add(self, units, date, value):
        value_str = sqlalchemy.cast(value, sqlalchemy.String)
        modifier = value_str.concat(f" {units}")
        return SQLFunction("DATE", date, modifier, type_=sqlalchemy.Date)

    def to_first_of_year(self, date):
        return SQLFunction("DATE", date, "start of year", type_=sqlalchemy.Date)

    def to_first_of_month(self, date):
        return SQLFunction("DATE", date, "start of month", type_=sqlalchemy.Date)

    def get_aggregate_subquery(self, aggregate_function, columns, return_type):
        # horrible edge-case where if a horizontal aggregate is called on
        # a single literal, sqlite will only return the first row
        if len(columns) == 1:
            return columns[0]
        # Sqlite returns null for greatest/least if any of the inputs are null
        # Use cyclic coalescence to remove the nulls before applying the aggregate function
        columns = get_cyclic_coalescence(columns)
        return aggregate_function(*columns)
