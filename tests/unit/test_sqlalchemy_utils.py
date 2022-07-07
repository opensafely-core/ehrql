import pytest
import sqlalchemy
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite

from databuilder.sqlalchemy_utils import (
    GeneratedTable,
    clause_as_str,
    get_setup_and_cleanup_queries,
    is_predicate,
)

table = sqlalchemy.Table(
    "some_table",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("i", type_=sqlalchemy.Integer()),
    sqlalchemy.Column("b", type_=sqlalchemy.Boolean()),
)

integer = table.c.i
boolean = table.c.b


@pytest.mark.parametrize(
    "expected,clause",
    [
        # All comparisons are predicates
        (True, integer == integer),
        (True, integer >= integer),
        (True, integer > integer),
        (True, integer < integer),
        (True, integer <= integer),
        (True, integer != integer),
        # As are boolean operations
        (True, boolean | boolean),
        (True, boolean & boolean),
        (True, ~boolean),
        # And combined boolean operations
        (True, ~(boolean & boolean)),
        (True, ~(boolean | boolean)),
        (True, ~boolean | ~boolean),
        (True, ~boolean & ~boolean),
        # And null checks
        (True, integer.is_(None)),
        (True, integer.is_not(None)),
        #
        # But not direct references to boolean columns
        (False, boolean),
        # Or other, non-boolean, binary operations
        (False, integer + integer),
        # Or arbitrary function calls
        (False, sqlalchemy.func.log10(integer)),
    ],
)
def test_is_predicate(expected, clause):
    assert is_predicate(clause) == expected, f"Expected {expected}: {clause}"


def test_get_setup_and_cleanup_queries_basic():
    # Make a temporary table
    temp_table = _make_temp_table("temp_table", "foo")
    temp_table.setup_queries.append(
        temp_table.insert().values(foo="bar"),
    )

    # Select something from it
    query = sqlalchemy.select(temp_table.c.foo)

    # Check that we get the right queries in the right order
    assert _queries_as_strs(query) == [
        "CREATE TABLE temp_table (\n\tfoo NULL\n)",
        "INSERT INTO temp_table (foo) VALUES (:foo)",
        "SELECT temp_table.foo \nFROM temp_table",
        "DROP TABLE temp_table",
    ]


def test_get_setup_and_cleanup_queries_nested():
    # Make a temporary table
    temp_table1 = _make_temp_table("temp_table1", "foo")
    temp_table1.setup_queries.append(
        temp_table1.insert().values(foo="bar"),
    )

    # Make a second temporary table ...
    temp_table2 = _make_temp_table("temp_table2", "baz")
    temp_table2.setup_queries.append(
        # ... populated by a SELECT query against the first table
        temp_table2.insert().from_select(
            [temp_table2.c.baz], sqlalchemy.select(temp_table1.c.foo)
        ),
    )

    # Select something from the second table
    query = sqlalchemy.select(temp_table2.c.baz)

    # Check that we create and drop the temporary tables in the right order
    assert _queries_as_strs(query) == [
        "CREATE TABLE temp_table1 (\n\tfoo NULL\n)",
        "INSERT INTO temp_table1 (foo) VALUES (:foo)",
        "CREATE TABLE temp_table2 (\n\tbaz NULL\n)",
        "INSERT INTO temp_table2 (baz) SELECT temp_table1.foo \nFROM temp_table1",
        "SELECT temp_table2.baz \nFROM temp_table2",
        "DROP TABLE temp_table2",
        "DROP TABLE temp_table1",
    ]


def _make_temp_table(name, *columns):
    table = GeneratedTable(
        name, sqlalchemy.MetaData(), *[sqlalchemy.Column(c) for c in columns]
    )
    table.setup_queries = [
        sqlalchemy.schema.CreateTable(table),
    ]
    table.cleanup_queries = [sqlalchemy.schema.DropTable(table)]
    return table


def _queries_as_strs(query):
    setup_queries, cleanup_queries = get_setup_and_cleanup_queries(query)
    return (
        [str(q).strip() for q in setup_queries]
        + [str(query).strip()]
        + [str(q).strip() for q in cleanup_queries]
    )


def test_clause_as_str():
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    query = sqlalchemy.select(table.c.bar).where(table.c.bar > 100)
    dialect = SQLiteDialect_pysqlite()
    query_str = clause_as_str(query, dialect)
    assert query_str == "SELECT foo.bar \nFROM foo \nWHERE foo.bar > 100"


# Converting CreateIndex to a string blows up without a special workaround
def test_clause_as_str_wtih_create_index():
    table = sqlalchemy.Table("foo", sqlalchemy.MetaData(), sqlalchemy.Column("bar"))
    index = sqlalchemy.Index(None, table.c.bar)
    create_index = sqlalchemy.schema.CreateIndex(index)
    dialect = SQLiteDialect_pysqlite()
    query_str = clause_as_str(create_index, dialect)
    assert query_str == "CREATE INDEX ix_foo_bar ON foo (bar)"
