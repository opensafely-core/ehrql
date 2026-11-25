import sqlalchemy

from ehrql.query_engines.sqlite_dialect import SQLiteDialect
from ehrql.utils.sqlalchemy_query_utils import clause_as_str


def test_bytes_literal_rendering():
    column = sqlalchemy.column("some_binary", sqlalchemy.types.VARBINARY())
    query = column == sqlalchemy.literal(b"\x01")
    assert clause_as_str(query, SQLiteDialect()) == "some_binary = X'01'"


def test_bytes_tuple_literal_rendering():
    column = sqlalchemy.column("some_binary", sqlalchemy.types.VARBINARY())
    query = column.in_(sqlalchemy.literal((b"\x00", b"\x01")))
    assert clause_as_str(query, SQLiteDialect()) == "some_binary IN (X'00', X'01')"
