import datetime
from functools import cached_property

import sqlalchemy.types
from sqlalchemy.dialects.mssql.base import MS_2008_VERSION
from sqlalchemy.dialects.mssql.pymssql import MSDialect_pymssql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable, cast


# MS-SQL can misinterpret ISO dates, depending on its localisation settings so
# we need to use particular date formats which we know will be consistently
# interpreted. We do this by defining custom SQLAlchemy types. See:
# https://github.com/opensafely-core/ehrql/issues/92
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
            return None
        assert isinstance(value, self.date_type)
        return value.strftime(self.format_str)

    def literal_processor(self, dialect):
        text_processor = self.text_type.literal_processor(dialect)

        def processor(value):
            # Use the bind param method above to convert to a string first
            value = self.process_bind_param(value, dialect)
            # Use the Text literal processor to quote and escape that string
            return text_processor(value)

        return processor

    def bind_expression(self, bindvalue):
        # Wrap any bound parameters in an explicit CAST to their intended type. MSSQL
        # (or at least the connection library we're using) doesn't let us pass in dates
        # as dates but insists on converting them to strings. Mostly this is harmless as
        # MSSQL can tell from the context that a date is required, but not always (see
        # issues below). Explicit CASTing ensures that they're always treated as dates.
        # https://github.com/opensafely-core/ehrql/pull/889
        # https://github.com/opensafely-core/ehrql/issues/998
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
# https://github.com/opensafely-core/ehrql/issues/1065
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


# Implement the "table value constructor trick" for applying an aggregation horizontally
# across columns. See:
# https://stackoverflow.com/questions/71022/sql-max-of-multiple-columns/6871572#6871572
#
# SQLAlchemy's ScalarSelect in combination with Values does almost exactly what we need
# here but it was obviously designed with the idea that the inputs to the table value
# constructor would be literal values rather than references to other columns. This
# means that it "loses" the references to these columns so that when you ask it e.g.
# what its children are or what tables it selects from, it gives the wrong answer. Here
# we subclass it and override methods to make it do the right thing.
class ScalarSelectAggregation(sqlalchemy.ScalarSelect):
    @classmethod
    def build(cls, aggregate_function, columns, **column_kwargs):
        new = cls.__new__(cls)
        new._orig_aggregate_function = aggregate_function
        new._orig_columns = columns
        new._orig_column_kwargs = column_kwargs
        new._init_scalar_select()
        return new

    def _init_scalar_select(self):
        # Set up `self` as if it were a properly constructed ScalarSelect object
        aggregate_function = self._orig_aggregate_function
        columns = self._orig_columns
        column_kwargs = self._orig_column_kwargs
        # We do this by constructing an appropriate ScalarSelect object ...
        values = sqlalchemy.values(
            sqlalchemy.Column("value", **column_kwargs), name="aggregate_values"
        ).data(
            [(column,) for column in columns],
        )
        aggregated = sqlalchemy.select(aggregate_function(values.columns[0]))
        scalar_select = aggregated.scalar_subquery()
        # ... and then copying its attributes across
        self.__dict__.update(scalar_select.__dict__)

    def get_children(self, **kwargs):
        yield from super().get_children(**kwargs)
        # When we iterate the query graph we need to be sure we include the column
        # references
        yield from self._orig_columns

    @cached_property
    def _from_objects(self):
        # Collect the "from" objects for every column
        all_froms = [
            obj for column in self._orig_columns for obj in column._from_objects
        ]
        # Return just the unique entries in their original order
        return list(dict.fromkeys(all_froms).keys())

    def _copy_internals(self, *, clone, **kwargs):
        # Ensure that this class can clone itself correctly
        self._orig_columns = [clone(column, **kwargs) for column in self._orig_columns]
        self._init_scalar_select()
