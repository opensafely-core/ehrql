import datetime
import secrets

import sqlalchemy
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable

from .base_sql import BaseSQLQueryEngine
from .spark_lib import SparkDate, SparkDialect


class CreateViewAs(Executable, ClauseElement):
    def __init__(self, name, query):
        self.name = name
        self.query = query

    def __str__(self):
        return str(self.query)


@compiles(CreateViewAs, "spark")
def _create_table_as(element, compiler, **kw):
    return "CREATE TEMPORARY VIEW %s AS %s" % (
        element.name,
        compiler.process(element.query),
    )


class SparkQueryEngine(BaseSQLQueryEngine):
    sqlalchemy_dialect = SparkDialect

    custom_types = {
        "date": SparkDate,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._temp_table_names = set()
        self._temp_table_prefix = "tmp_{today}_{random}_".format(
            today=datetime.date.today().strftime("%Y%m%d"),
            random=secrets.token_hex(6),
        )

    def write_query_to_table(self, table, query):
        """
        Returns a new query which, when executed, writes the results of `query`
        into `table`
        """
        return CreateViewAs(table.name, query)

    def get_temp_table_name(self, table_name):
        """
        Return a table name based on `table_name` but suitable for use as a
        temporary table.

        It's the caller's responsibility to ensure `table_name` is unique
        within this session; it's this function's responsibility to ensure it
        doesn't clash with any concurrent extracts
        """
        temp_table_name = f"{self._temp_table_prefix}{table_name}"
        self._temp_table_names.add(temp_table_name)
        return temp_table_name

    def post_execute_cleanup(self, cursor):
        """
        Called after results have been fetched
        """
        for table_name in self._temp_table_names:
            table = sqlalchemy.Table(table_name, sqlalchemy.MetaData())
            query = sqlalchemy.schema.DropTable(table, if_exists=True)
            cursor.execute(query)
