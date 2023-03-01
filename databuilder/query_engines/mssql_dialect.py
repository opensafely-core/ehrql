import datetime

import sqlalchemy.types
from sqlalchemy.dialects.mssql.base import MS_2008_VERSION
from sqlalchemy.dialects.mssql.pymssql import MSDialect_pymssql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable, cast


# MS-SQL can misinterpret ISO dates, depending on its localisation settings so
# we need to use particular date formats which we know will be consistently
# interpreted. We do this by defining custom SQLAlchemy types. See:
# https://github.com/opensafely-core/databuilder/issues/92
# http://msdn.microsoft.com/en-us/library/ms180878.aspx
# https://stackoverflow.com/a/25548626/559140
class _MSSQLDateTimeBase:
    text_type = sqlalchemy.types.Text()

    def process_bind_param(self, value, dialect):
        """
        Convert a Python value to a form suitable for passing as a parameter to
        the database connector
        """
        if value is None:
            # TODO: test this branch
            return None  # pragma: no cover
        # We accept ISO formated strings as well
        if isinstance(value, str):
            value = self.date_type.fromisoformat(value)
        if not isinstance(value, self.date_type):
            raise TypeError(f"Expected {self.date_type} or str got: {value!r}")
        return value.strftime(self.format_str)

    def process_literal_param(self, value, dialect):
        """
        Convert a Python value into an escaped string suitable for
        interpolating directly into an SQL string
        """
        # Use the above method to convert to a string first
        value = self.process_bind_param(value, dialect)
        # Use the Text literal processor to quote and escape that string
        literal_processor = self.text_type.literal_processor(dialect)
        return literal_processor(value)

    def bind_expression(self, bindvalue):
        # Wrap any bound parameters in an explicit CAST to their intended type. MSSQL
        # (or at least the connection library we're using) doesn't let us pass in dates
        # as dates but insists on converting them to strings. Mostly this is harmless as
        # MSSQL can tell from the context that a date is required, but not always (see
        # issues below). Explicit CASTing ensures that they're always treated as dates.
        # https://github.com/opensafely-core/databuilder/pull/889
        # https://github.com/opensafely-core/databuilder/issues/998
        return cast(bindvalue, type_=self)


class MSSQLDate(_MSSQLDateTimeBase, sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.Date
    cache_ok = True
    date_type = datetime.date
    # See https://stackoverflow.com/a/25548626/559140
    format_str = "%Y%m%d"


class MSSQLDateTime(_MSSQLDateTimeBase, sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.DateTime
    cache_ok = True
    date_type = datetime.datetime
    # See https://stackoverflow.com/a/25548626/559140
    format_str = "%Y-%m-%dT%H:%M:%S"


# MS-SQL can interpret values that we intend to be floats as Decimals, which
# can result in results with unexpectedly truncated precision.
# https://github.com/opensafely-core/databuilder/issues/1065
# https://learn.microsoft.com/en-us/sql/t-sql/data-types/precision-scale-and-length-transact-sql
class MSSQLFloat(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.Float
    cache_ok = True

    def bind_expression(self, bindvalue):
        # Wrap any bound parameters in an explicit CAST to their intended type.
        # This ensures that any float-like numbers are always cast to
        # floats, otherwise MSSQL will sometimes make a best-guess and return a
        # Decimal type, which behaves differently to other engine.
        return cast(bindvalue, type_=self)


class MSSQLDialect(MSDialect_pymssql):
    supports_statement_cache = True

    colspecs = MSDialect_pymssql.colspecs | {
        sqlalchemy.types.Date: MSSQLDate,
        sqlalchemy.types.DateTime: MSSQLDateTime,
        sqlalchemy.types.Float: MSSQLFloat,
    }

    # The base MSSQL dialect generates different SQL depending on the version of SQL
    # Server it thinks it's talking to. If it's not yet connected to any database it
    # defaults to the 2005 version. This means that the SQL generated locally by
    # `dump-dataset-sql` doesn't match what actually gets executed. Here we set a
    # minimum version which we use as the default, and check that any server we connect
    # to meets this minimum. You can see the versions available, and which features are
    # switched on them, in this file:
    # https://github.com/sqlalchemy/sqlalchemy/blob/rel_1_4_46/lib/sqlalchemy/dialects/mssql/base.py#L912-L919
    minimum_server_version = MS_2008_VERSION

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_version_info = self.minimum_server_version

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        if self.server_version_info < self.minimum_server_version:
            raise RuntimeError(
                f"SQL Server has version {self.server_version_info} but we require at "
                f"least {self.minimum_server_version}"
            )


class SelectStarInto(Executable, ClauseElement):
    inherit_cache = True

    def __init__(self, table, selectable):
        self.table = table
        self.selectable = selectable

    def get_children(self):
        return (self.table, self.selectable)


@compiles(SelectStarInto)
def visit_select_star_into(element, compiler, **kw):
    return "SELECT * INTO {} FROM {}".format(
        compiler.process(element.table, asfrom=True, **kw),
        compiler.process(element.selectable, asfrom=True, **kw),
    )
