import logging

import sqlalchemy
from sqlalchemy.sql.functions import Function as SQLFunction

from ehrql.query_engines.base_sql import BaseSQLQueryEngine, get_cyclic_coalescence
from ehrql.query_engines.trino_dialect import TrinoDialect
from ehrql.query_model.nodes import Position
from ehrql.utils.sqlalchemy_query_utils import (
    CreateTableAs,
    GeneratedTable,
    InsertMany,
)


log = logging.getLogger()


class TrinoQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = TrinoDialect

    def get_order_clauses(self, sort_conditions, position):
        order_clauses = super().get_order_clauses(sort_conditions, position)
        # Trino always sorts with nulls last by default. We need ascending sorts to
        # sort with nulls first
        if position == Position.FIRST:
            order_clauses = [sqlalchemy.nullsfirst(c) for c in order_clauses]
        return order_clauses

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

    def cast_to_int(self, value):
        # Trino's casting to int rounds away from zero. We need to round towards zero for
        # consistency with other query engines.
        rounded_towards_zero = sqlalchemy.case(
            (value > 0, SQLFunction("FLOOR", value)),
            else_=SQLFunction("CEILING", value),
        )
        return sqlalchemy.cast(rounded_towards_zero, sqlalchemy.Integer)

    def truedivide(self, lhs, rhs):
        rhs_null_if_zero = SQLFunction("NULLIF", rhs, 0.0, type_=sqlalchemy.Float)
        return lhs / rhs_null_if_zero

    @property
    def aggregate_functions(self):
        return {
            "minimum_of": sqlalchemy.func.least,
            "maximum_of": sqlalchemy.func.greatest,
        }

    def get_aggregate_subquery(self, aggregate_function, columns, return_type):
        # Trino returns null for greatest/least if any of the inputs are null
        # Use cyclic coalescence to remove the nulls before applying the aggregate function
        columns = get_cyclic_coalescence(columns)
        return aggregate_function(*columns)

    def create_inline_table(self, columns, rows):
        # Trino doesn't support temporary tables, so we create
        # a new persistent table and drop it in the cleanup
        # queries
        table_name = f"ehrql_{self.global_unique_id}_inline_data_{self.get_next_id()}"
        columns, rows = self.backend.modify_inline_table_args(columns, rows)
        table = GeneratedTable(
            table_name,
            sqlalchemy.MetaData(),
            *columns,
        )
        table.setup_queries = [
            sqlalchemy.schema.CreateTable(table),
            InsertMany(table, rows),
        ]
        table.cleanup_queries = [
            sqlalchemy.schema.DropTable(table),
        ]
        return table

    def reify_query(self, query):
        table_name = f"ehrql_{self.global_unique_id}_tmp_{self.get_next_id()}"
        query = self.backend.modify_query_pre_reify(query)
        table = GeneratedTable.from_query(table_name, query)
        table.setup_queries = [
            CreateTableAs(table, query),
        ]
        table.cleanup_queries = [
            sqlalchemy.schema.DropTable(table, if_exists=True),
        ]
        return table
