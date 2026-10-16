from types import SimpleNamespace

import sqlalchemy

from ehrql.query_engines.base_sql import before_cursor_execute_add_comment
from ehrql.utils.sqlalchemy_query_utils import add_comment_to_query


def test_before_cursor_execute_add_comment():
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    query = add_comment_to_query(sqlalchemy.select(table.c.bar), "some comment")
    context = SimpleNamespace(compiled=SimpleNamespace(statement=query))

    statement, parameters = before_cursor_execute_add_comment(
        connection=None,
        cursor=None,
        statement="SELECT foo.bar FROM foo",
        parameters=None,
        context=context,
        executemany=False,
    )

    assert statement == "-- some comment\nSELECT foo.bar FROM foo"
    assert parameters is None


def test_before_cursor_execute_add_comment_with_no_comment():
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    query = sqlalchemy.select(table.c.bar)
    context = SimpleNamespace(compiled=SimpleNamespace(statement=query))

    statement, parameters = before_cursor_execute_add_comment(
        connection=None,
        cursor=None,
        statement="SELECT foo.bar FROM foo",
        parameters=None,
        context=context,
        executemany=False,
    )

    assert statement == "SELECT foo.bar FROM foo"


def test_before_cursor_execute_add_comment_with_no_compiled_context():
    # DDL execution contexts don't always expose `.compiled`; confirm we don't blow
    # up in that case
    context = SimpleNamespace(compiled=None)

    statement, parameters = before_cursor_execute_add_comment(
        connection=None,
        cursor=None,
        statement="SELECT 1",
        parameters=None,
        context=context,
        executemany=False,
    )

    assert statement == "SELECT 1"
