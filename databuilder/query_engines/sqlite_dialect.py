import datetime

import sqlalchemy.types
from sqlalchemy.dialects.sqlite.pysqlite import (
    SQLiteDialect_pysqlite,
    _SQLite_pysqliteDate,
)


class SQLiteDate(sqlalchemy.types.TypeDecorator):
    impl = _SQLite_pysqliteDate
    cache_ok = True

    def process_bind_param(self, value, dialect):
        # This makes inserting test data into SQLite slightly easier by letting it
        # accept ISO formatted strings as dates, as the other database engines do.
        # Otherwise we get the error:
        #
        #   SQLite Date type only accepts Python date objects as input
        #
        if isinstance(value, str):
            return datetime.date.fromisoformat(value)
        else:
            return value


class SQLiteDialect(SQLiteDialect_pysqlite):

    supports_statement_cache = True

    colspecs = SQLiteDialect_pysqlite.colspecs | {
        sqlalchemy.types.Date: SQLiteDate,
    }

    def do_on_connect(self, connection):
        # Set the per-connection flag which makes LIKE queries case-sensitive
        connection.execute("PRAGMA case_sensitive_like = 1;")

    def on_connect(self):
        # `on_connect` must return a callable to be executed
        return self.do_on_connect
