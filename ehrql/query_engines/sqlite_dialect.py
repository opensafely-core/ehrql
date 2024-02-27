import sqlean
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite


class SQLiteDialect(SQLiteDialect_pysqlite):
    supports_statement_cache = False

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
