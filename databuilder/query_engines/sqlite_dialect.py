import datetime

import sqlalchemy.types
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite


class SQLiteDateTimeBase:
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
        return value

    def process_literal_param(self, value, dialect):
        """
        Convert a Python value into an escaped string suitable for
        interpolating directly into an SQL string
        """
        # Use the above method to convert to a date/datetime first
        value = self.process_bind_param(value, dialect)
        # Format as a string
        value_str = value.isoformat()
        # Use the Text literal processor to quote and escape that string
        literal_processor = self.text_type.literal_processor(dialect)
        return literal_processor(value_str)


class SQLiteDate(SQLiteDateTimeBase, sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.Date
    cache_ok = True
    date_type = datetime.date

    def process_result_value(self, value, dialect):
        # SQLite gives us strings but we want dates
        #
        # If the underlying database type is a DATETIME then that's what we'll get back,
        # even if we've cast it to a DATE in our schema. So we convert datetime strings
        # to dates by truncating.
        if value is not None:
            value = value[:10]
            return self.date_type.fromisoformat(value)


class SQLiteDateTime(SQLiteDateTimeBase, sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.DateTime
    cache_ok = True
    date_type = datetime.datetime

    def process_result_value(self, value, dialect):
        return self.date_type.fromisoformat(value)


class SQLiteDialect(SQLiteDialect_pysqlite):
    colspecs = SQLiteDialect_pysqlite.colspecs | {
        sqlalchemy.types.Date: SQLiteDate,
        sqlalchemy.types.DateTime: SQLiteDateTime,
    }
