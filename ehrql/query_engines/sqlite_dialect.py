import sqlalchemy.types
import sqlean
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite


class SQLiteBinary(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.LargeBinary
    cache_ok = True

    def literal_processor(self, _dialect):
        def process(value):
            # SQLite spells binary literals X'ABCD'
            return "X'" + value.hex() + "'"

        return process


class SQLiteDialect(SQLiteDialect_pysqlite):
    supports_statement_cache = False

    colspecs = SQLiteDialect_pysqlite.colspecs | {
        sqlalchemy.types.LargeBinary: SQLiteBinary,
        sqlalchemy.types.VARBINARY: SQLiteBinary,
    }

    @classmethod
    def import_dbapi(cls):
        # Use sqlean rather than the system version
        sqlean.extensions.enable("math")
        return sqlean.dbapi2

    def do_on_connect(self, connection):
        # Set the per-connection flag which makes LIKE queries case-sensitive
        connection.execute("PRAGMA case_sensitive_like = 1;")

    def on_connect(self):
        # `on_connect` must return a callable to be executed
        return self.do_on_connect
