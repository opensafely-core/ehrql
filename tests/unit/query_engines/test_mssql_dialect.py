import datetime

import sqlalchemy
from sqlalchemy.sql.visitors import iterate, replacement_traverse

from ehrql.query_engines.mssql_dialect import (
    MSSQLDialect,
    ScalarSelectAggregation,
    SelectStarInto,
)


def test_mssql_date_types():
    # Note: it would be nice to parameterize this test, but given that the
    # inputs are SQLAlchemy expressions I don't know how to do this without
    # constructing the column objects outside of the test, which I don't really
    # want to do.
    date_col = sqlalchemy.Column("date_col", sqlalchemy.Date())
    datetime_col = sqlalchemy.Column("datetime_col", sqlalchemy.DateTime())
    assert (
        _str(date_col == datetime.date(2021, 5, 15))
        == "date_col = CAST('20210515' AS DATE)"
    )
    assert (
        _str(datetime_col == datetime.datetime(2021, 5, 15, 9, 10, 0))
        == "datetime_col = CAST('2021-05-15T09:10:00' AS DATETIME)"
    )
    assert _str(date_col == None) == "date_col IS NULL"  # noqa: E711
    assert _str(datetime_col == None) == "datetime_col IS NULL"  # noqa: E711


def test_casts_to_date():
    # This fails unless our MSSQL dialect sets the appropriate minimum server version.
    # By default it will treat DATE as an alias for DATETIME. See:
    # https://github.com/sqlalchemy/sqlalchemy/blob/rel_1_4_46/lib/sqlalchemy/dialects/mssql/base.py#L1623-L1627
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    clause = sqlalchemy.cast(table.c.bar, sqlalchemy.Date)
    compiled = str(clause.compile(dialect=MSSQLDialect()))
    assert compiled == "CAST(foo.bar AS DATE)"


def test_select_star_into():
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    query = sqlalchemy.select(table.c.bar).where(table.c.bar > 1)
    target_table = sqlalchemy.table("test")
    select_into = SelectStarInto(target_table, query.alias())
    assert _str(select_into) == (
        "SELECT * INTO test FROM (SELECT foo.bar AS bar \n"
        "FROM foo \n"
        "WHERE foo.bar > 1) AS anon_1"
    )


def test_select_star_into_can_be_iterated():
    # If we don't define the `get_children()` method on `SelectStarInto` we won't get an
    # error when attempting to iterate the resulting element structure: it will just act
    # as a leaf node. But as we rely heavily on query introspection we need to ensure we
    # can iterate over query structures.
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    query = sqlalchemy.select(table.c.bar).where(table.c.bar > 1)
    target_table = sqlalchemy.table("test")
    select_into = SelectStarInto(target_table, query.alias())

    # Check that SelectStarInto supports iteration by confirming that we can get back to
    # both the target table and the original table by iterating it
    assert any([e is table for e in iterate(select_into)]), "no `table`"
    assert any([e is target_table for e in iterate(select_into)]), "no `target_table`"


def _str(expression):
    compiled = expression.compile(
        dialect=MSSQLDialect(),
        compile_kwargs={"literal_binds": True},
    )
    return str(compiled).strip()


def test_mssql_float_type():
    float_col = sqlalchemy.Column("float_col", sqlalchemy.Float())
    # explicitly casts floats
    assert _str(float_col == 0.75) == "float_col = CAST(0.75 AS FLOAT)"
    assert _str(float_col == None) == "float_col IS NULL"  # noqa: E711
    assert (
        _str(sqlalchemy.sql.case((float_col > 0.5, 0.1), else_=0.75))
        == "CASE WHEN (float_col > CAST(0.5 AS FLOAT)) THEN CAST(0.1 AS FLOAT) ELSE CAST(0.75 AS FLOAT) END"
    )


def test_scalar_select_aggregation():
    table = sqlalchemy.table(
        "t1",
        sqlalchemy.Column("c1"),
        sqlalchemy.Column("c2"),
        sqlalchemy.Column("c3"),
    )
    maximum = ScalarSelectAggregation.build(
        sqlalchemy.func.max, [table.columns.c1, table.columns.c2]
    )
    query = sqlalchemy.select(table.columns.c3).where(maximum == 1)
    assert _str(query) == (
        "SELECT t1.c3 \n"
        "FROM t1 \n"
        "WHERE ("
        "SELECT max(aggregate_values.value) AS max_1 \n"
        "FROM (VALUES (t1.c1), (t1.c2)) AS aggregate_values (value)"
        ") = 1"
    )


def test_scalar_select_aggregation_can_be_iterated():
    table = sqlalchemy.table(
        "t1",
        sqlalchemy.Column("c1"),
        sqlalchemy.Column("c2"),
        sqlalchemy.Column("c3"),
    )
    maximum = ScalarSelectAggregation.build(
        sqlalchemy.func.max, [table.columns.c1, table.columns.c2]
    )
    query = sqlalchemy.select(table.columns.c3).where(maximum == 1)
    # Check that iterating the resulting query gets us back to the original columns
    iterator_elements = iterate(query)
    expected = [table.columns.c1, table.columns.c2, table.columns.c3]
    # We have to compare object IDs here because these objects overload `__eq__`
    assert {id(el) for el in expected} <= {id(el) for el in iterator_elements}


def test_scalar_select_aggregation_supports_replacement_traverse():
    table = sqlalchemy.table(
        "t1",
        sqlalchemy.Column("c1"),
        sqlalchemy.Column("c2"),
        sqlalchemy.Column("c3"),
    )
    query = ScalarSelectAggregation.build(
        sqlalchemy.func.max, [table.columns.c1, table.columns.c2]
    )
    new_query = replacement_traverse(
        query,
        {},
        lambda obj: table.columns.c3 if obj is table.columns.c2 else None,
    )
    assert _str(query) == (
        "(SELECT max(aggregate_values.value) AS max_1 \n"
        "FROM (VALUES (t1.c1), (t1.c2)) AS aggregate_values (value))"
    )
    assert _str(new_query) == (
        "(SELECT max(aggregate_values.value) AS max_1 \n"
        "FROM (VALUES (t1.c1), (t1.c3)) AS aggregate_values (value))"
    )
