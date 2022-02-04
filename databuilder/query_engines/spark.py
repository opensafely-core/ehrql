import datetime
import secrets

import sqlalchemy
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable, type_coerce

from .. import sqlalchemy_types
from .base_sql import BaseSQLQueryEngine
from .spark_dialect import SparkDialect


class CreateViewAs(Executable, ClauseElement):
    def __init__(self, name, query):
        self.name = name
        self.query = query

    def __str__(self):
        return str(self.query)

    def get_children(self):
        return (self.query,)


@compiles(CreateViewAs, "spark")
def _create_table_as(element, compiler, **kw):
    return "CREATE TEMPORARY VIEW {} AS {}".format(
        element.name,
        compiler.process(element.query),
    )


class SparkQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = SparkDialect

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a unique prefix for temporary tables. Including the date makes it
        # easier to clean this up by hand later if we have to.
        self.temp_table_prefix = "tmp_{today}_{random}_".format(
            today=datetime.date.today().strftime("%Y%m%d"),
            random=secrets.token_hex(6),
        )

    def query_to_create_temp_table_from_select_query(self, table, select_query):
        """
        Return a query to create `table` and populate it with the results of
        `select_query`
        """
        return CreateViewAs(table.name, select_query)

    def temp_table_needs_dropping(self, create_table_query):
        # The views we create are temporary and don't require dropping
        if isinstance(create_table_query, CreateViewAs):
            return False
        # Anything else is a regular table which does require dropping
        return True

    def get_temp_database(self):
        return self.backend.temporary_database

    def _convert_date_diff_to_days(
        self, start, end
    ):  # pragma: no cover (re-implement when the QL is in)
        """
        Calculate difference in days
        The sparkSQL datediff function only calculate diff in days, and take the
        parameters in the order (end, start)
        """
        return sqlalchemy.func.datediff(end, start)

    def date_add(
        self, start_date, number_of_days
    ):  # pragma: no cover (re-implement when the QL is in)
        """
        Add a number of days to a date, using the `dateadd` function
        The sparkSQL date_add function only allows adding days
        """
        start_date = type_coerce(start_date, sqlalchemy_types.Date())
        return type_coerce(
            sqlalchemy.func.date_add(start_date, number_of_days),
            sqlalchemy_types.Date(),
        )

    def date_subtract(
        self, start_date, number_of_days
    ):  # pragma: no cover (re-implement when the QL is in)
        """
        Subtract a number of days from a date, using the `date_add` function
        """
        start_date = type_coerce(start_date, sqlalchemy_types.Date())
        return type_coerce(
            sqlalchemy.func.date_add(start_date, number_of_days * -1),
            sqlalchemy_types.Date(),
        )

    def round_to_first_of_month(
        self, date
    ):  # pragma: no cover (re-implement when the QL is in)
        date = type_coerce(date, sqlalchemy_types.Date())

        first_of_month = sqlalchemy.func.date_trunc(
            "MONTH",
            date,
        )
        return type_coerce(first_of_month, sqlalchemy_types.Date())

    def round_to_first_of_year(
        self, date
    ):  # pragma: no cover (re-implement when the QL is in)
        date = type_coerce(date, sqlalchemy_types.Date())

        first_of_year = sqlalchemy.func.date_trunc(
            "YEAR",
            date,
        )

        return type_coerce(first_of_year, sqlalchemy_types.Date())
