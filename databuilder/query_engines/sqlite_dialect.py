from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite


class SQLiteDialect(SQLiteDialect_pysqlite):
    supports_statement_cache = True

    # Use the `named` parameter placeholder style for consistency with other dialects.
    # SQLite supports this alongside several others:
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.paramstyle
    default_paramstyle = "named"

    def do_on_connect(self, connection):
        # Set the per-connection flag which makes LIKE queries case-sensitive
        connection.execute("PRAGMA case_sensitive_like = 1;")

    def on_connect(self):
        # `on_connect` must return a callable to be executed
        return self.do_on_connect
