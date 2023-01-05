import sqlalchemy
from sqlalchemy.sql.visitors import iterate

from databuilder.query_engines.spark_dialect import CreateTemporaryViewAs


def test_create_temporary_view_as():  # pragma: cover-spark-only
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    query = sqlalchemy.select(table.c.bar).where(table.c.bar > 1)
    target_table = sqlalchemy.table("test")
    create_view = CreateTemporaryViewAs(target_table, query)
    assert str(create_view).strip() == (
        "CREATE TEMPORARY VIEW test AS SELECT foo.bar \n"
        "FROM foo \n"
        "WHERE foo.bar > :bar_1"
    )


def test_create_temporary_view_as_can_be_iterated():  # pragma: cover-spark-only
    # If we don't define the `get_children()` method on `CreateTemporaryViewAs` we won't
    # get an error when attempting to iterate the resulting element structure: it will
    # just act as a leaf node. But as we rely heavily on query introspection we need to
    # ensure we can iterate over query structures.
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    query = sqlalchemy.select(table.c.bar).where(table.c.bar > 1)
    target_table = sqlalchemy.table("test")
    create_view = CreateTemporaryViewAs(target_table, query)

    # Check that element supports iteration by confirming that we can get back to both
    # the target table and the original table by iterating it
    assert any([e is table for e in iterate(create_view)]), "no `table`"
    assert any([e is target_table for e in iterate(create_view)]), "no `target_table`"
