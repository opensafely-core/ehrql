"""
Provides a SQLAlchemy Dialect for talking to a Spark database which uses the
dialect provided by pyhive with a layer of customisations and fixes on top.

The majority of these fixes are only relevant to the ORM layer, which we only
use for test setup and not in production. Hence I'm less bothered than I might
otherwise be about how fragile they are.
"""
import datetime
import re

import databricks.sql
import sqlalchemy.types
from pyhive.sqlalchemy_hive import HiveHTTPDialect, HiveTypeCompiler, _type_map
from sqlalchemy import String, exc, types, util
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.compiler import DDLCompiler, IdentifierPreparer
from sqlalchemy.sql.expression import ClauseElement, Executable, cast


class CreateTemporaryViewAs(Executable, ClauseElement):
    def __init__(self, table, query):
        self.table = table
        self.query = query

    def get_children(self):
        return (self.table, self.query)


@compiles(CreateTemporaryViewAs)
def visit_create_temporary_view_as(element, compiler, **kw):
    return "CREATE TEMPORARY VIEW {} AS {}".format(
        compiler.process(element.table, asfrom=True, **kw),
        compiler.process(element.query, **kw),
    )


class SparkDate(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.Date

    def process_result_value(self, value, dialect):
        """
        Without this we get dates returned as strings rather than
        `datetime.date` objects as we expect
        """
        # databricks sql DBAPI returns a date object so we need this branch but it's not
        # hit in our local tests
        if isinstance(value, datetime.date):  # pragma: no cover
            return value
        elif isinstance(value, str):
            return sqlalchemy.processors.str_to_date(value)
        elif value is None:
            return None
        else:  # pragma: no cover
            raise TypeError(f"Unhandled date type: {value}")

    def bind_expression(self, bindvalue):
        """
        Spark won't accept date strings in INSERT statements unless we
        explicity cast them to dates
        """
        return cast(bindvalue, type_=self)


class SparkDateTime(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.DateTime

    # I expect this is end up being covered once we promote Spark from a "legacy"
    # dialect to one included in the default engine fixture
    def bind_expression(self, bindvalue):  # pragma: no cover
        """
        Spark won't accept datetime strings in INSERT statements unless we
        explicity cast them to datetimes
        """
        return cast(bindvalue, type_=self)


class SparkDDLCompiler(DDLCompiler):
    def visit_primary_key_constraint(self, constraint, **kw):
        """
        Prevent SQLAlchemy from trying to create PRIMARY KEY constraints, which
        Spark doesn't support. There's already some attempt to address this in
        pyhive but we need this as well, presumably because using the DDL to
        create tables isn't part of the standard use case. See:

        https://github.com/dropbox/PyHive/blob/b21c507a24/pyhive/sqlalchemy_hive.py#L338-L340

        This is only required by the SQLAlchemy ORM layer and therefore only
        used in test.
        """
        return ""


class SparkTypeCompiler(HiveTypeCompiler):
    def visit_DATE(self, type_):
        """
        For some reason pyhive treats DATE as TIMESTAMP, as it does for
        DATETIME. I'm not sure if this is just a bug or if there's some other
        reason behind it. See:

        https://github.com/dropbox/PyHive/blob/b21c507a24/pyhive/sqlalchemy_hive.py#L200-L201
        """
        return "DATE"


class SparkIdentifierPreparer(IdentifierPreparer):
    """
    pyhive quotes all identifiers, whether they're reserved words or not. This
    makes some already tricky to read SQL even harder to read, so we just use
    the default list of reserved words here.  We also supply the correct quote
    escape character which pyhive omits. See:

    https://github.com/dropbox/PyHive/blob/b21c507a24/pyhive/sqlalchemy_hive.py#L111-L119
    """

    def __init__(self, dialect):
        super().__init__(dialect, initial_quote="`", escape_quote="`")


class SparkDialect(HiveHTTPDialect):
    """Customisation of the base pyhive Sqlalchemy dialect.

    Some customisations are generic Spark SQL fixes that we want to handle
    differently from the pyhive dialect: the date handling, basically.

    Other customisations are to support using the Sqlalchemy ORM with this
    dialect, which pyhive doesn't fully support out of the box, but we use in
    our tests. This is the primary key DDL and Identifier changes, and the
    exception/connection wrapping.

    The last customisation is to support connecting to a Databricks hosted
    instance of Spark, which requires using a different DBAPI and connection
    arguments, but otherwise is the same.
    """

    name = "spark"

    ddl_compiler = SparkDDLCompiler
    type_compiler = SparkTypeCompiler
    preparer = SparkIdentifierPreparer

    # PyHive has `True` below which doesn't do what they think it does. I considered
    # submitting a fix, but this is all going away in newer versions of SQLAlchemy so I
    # don't think it's worth it. See:
    # https://github.com/sqlalchemy/sqlalchemy/commit/bd2a6e9b161251606b64d299faec583d
    returns_unicode_strings = String.RETURNS_UNICODE

    colspecs = HiveHTTPDialect.colspecs | {
        sqlalchemy.types.Date: SparkDate,
        sqlalchemy.types.DateTime: SparkDateTime,
    }

    # This function is only excercised when manually running the tests against databricks
    def create_connect_args(self, url):  # pragma: no cover
        """Switch between generic phyive DBAPI and databricks DBAPI as needed.

        We use the generic pyhive DBAPI to talke to a local spark container in
        regular tests, but we use the Databricks api in integration tests and
        production.

        The only significate difference in API is the format of the connection
        arguments, and that the databricks DBAPI uses async thrift.
        """

        if "http_path" not in url.query:
            # regular pyhive connection
            return super().create_connect_args(url)

        # databricks connection
        #
        # Switch to use databricks pyhive based-DBAPI reather than the default
        # This is not very clean, but its simple and it seems to work.
        self.dbapi = databricks.sql

        server_hostname = url.host
        http_path = url.query["http_path"]

        # TODO: handle access_token
        kwargs = {
            # secret undocumented auth
            "_username": url.username,
            "_password": url.password,
        }

        return (server_hostname, http_path, None), kwargs

    # All the remaining changes are only required to get the SQLAlchemy ORM
    # layer to work, which we only use for test setup

    def _get_table_columns(self, connection, table_name, schema):
        """
        For the SQLAlchemy ORM to function correctly we need to translate
        "table not found" errors into the appropriate exception. pyhive uses
        string matching for this and the format of the error messages in the
        specific version of Spark/Hive we are using doesn't match. See:

        https://github.com/dropbox/PyHive/blob/b21c507a24/pyhive/sqlalchemy_hive.py#L275-L297
        """
        connection = ConnectionWrapper(connection)
        try:
            return super()._get_table_columns(connection, table_name, schema)
        except exc.OperationalError as e:
            full_table = table_name if not schema else f"{schema}.{table_name}"
            if "Table or view not found" in str(e):  # pragma: no cover
                raise exc.NoSuchTableError(full_table)
            else:
                raise

    # We do not currently use this function in our code, but we might in future.
    # It is taken from:
    # https://github.com/crflynn/databricks-dbapi/blob/master/databricks_dbapi/sqlalchemy_dialects/base.py#L17
    def get_columns(
        self, connection, table_name, schema=None, **kw
    ):  # pragma: no cover
        """Get columns according to Databricks' hive or oss hive."""
        rows = self._get_table_columns(connection, table_name, schema)
        # Strip whitespace
        rows = [[col.strip() if col else None for col in row] for row in rows]
        # Filter out empty rows and comment
        rows = [row for row in rows if row[0] and row[0] != "# col_name"]
        result = []
        for (col_name, col_type, _comment) in rows:
            # Note: this next line is the only change from pyhive's verion of
            # this function as of 2021-11-29.
            #
            # Handle both oss hive and Databricks' hive partition header, respectively
            if col_name in ("# Partition Information", "# Partitioning"):
                break
            # Take out the more detailed type information
            # e.g. 'map<int,int>' -> 'map'
            #      'decimal(10,1)' -> decimal
            col_type = re.search(r"^\w+", col_type).group(0)
            try:
                coltype = _type_map[col_type]
            except KeyError:
                util.warn(
                    "Did not recognize type '{}' of column '{}'".format(
                        col_type, col_name
                    )
                )
                coltype = types.NullType

            result.append(
                {
                    "name": col_name,
                    "type": coltype,
                    "nullable": True,
                    "default": None,
                }
            )
        return result


class ConnectionWrapper:
    """
    When running in "future" mode SQLAlchemy connections will no longer execute
    raw SQL strings. Instead these must be explictly wrapped up as "text" query
    object. To avoid having to configure our connections to use legacy mode, we
    re-implement the old behaviour here.
    """

    def __init__(self, connection):
        self.connection = connection

    def execute(self, arg, **kwargs):
        if isinstance(arg, str):  # pragma: no cover
            arg = sqlalchemy.text(arg)
        return self.connection.execute(arg, **kwargs)
