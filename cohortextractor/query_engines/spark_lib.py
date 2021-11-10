"""
Provides a SQLAlchemy Dialect for talking to a Spark database which uses the
dialect provided by pyhive with a layer of customisations and fixes on top.

The majority of these fixes are only relevant to the ORM layer, which we only
use for test setup and not in production. Hence I'm less bothered than I might
otherwise be about how fragile they are.
"""
import sqlalchemy.types
from pyhive.sqlalchemy_hive import HiveHTTPDialect, HiveTypeCompiler
from sqlalchemy import exc
from sqlalchemy.sql.compiler import DDLCompiler, IdentifierPreparer
from sqlalchemy.sql.expression import cast


class SparkDate(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.Date

    def process_result_value(self, value, dialect):
        """
        Without this we get dates returned as strings rather than
        `datetime.date` objects as we expect
        """
        return sqlalchemy.processors.str_to_date(value)

    def bind_expression(self, bindvalue):
        """
        Spark won't accept date strings in INSERT statements unless we
        explicity cast them to dates
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
    name = "spark"

    ddl_compiler = SparkDDLCompiler
    type_compiler = SparkTypeCompiler
    preparer = SparkIdentifierPreparer

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
            if "Table or view not found" in str(e):
                raise exc.NoSuchTableError(full_table)
            else:
                raise

    def get_schema_names(self, connection, *args, **kwargs):
        connection = ConnectionWrapper(connection)
        return super().get_schema_names(connection, *args, **kwargs)

    def get_table_names(self, connection, *args, **kwargs):
        connection = ConnectionWrapper(connection)
        return super().get_table_names(connection, *args, **kwargs)


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
        if isinstance(arg, str):
            arg = sqlalchemy.text(arg)
        return self.connection.execute(arg, **kwargs)
