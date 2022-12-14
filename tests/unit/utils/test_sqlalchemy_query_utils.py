import pytest
import sqlalchemy
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.engine.default import DefaultDialect

from databuilder.utils.sqlalchemy_query_utils import (
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
    query_str = clause_as_str(query, DefaultDialect())
    assert query_str == "SELECT foo.bar \nFROM foo \nWHERE foo.bar > 100"


def test_clause_as_str_with_create_index_on_sqlite():
    # This test confirms the presence of a SQLAlchemy bug which we have to work around
    # in `clause_as_str` by compiling the query twice: once without the
    # `render_postcompile` argument, and then again with the argument if it's needed. If
    # the bug gets fixed we want to know so that we can remove the workaround.

    table = sqlalchemy.Table("foo", sqlalchemy.MetaData(), sqlalchemy.Column("bar"))
    index = sqlalchemy.Index(None, table.c.bar)
    create_index = sqlalchemy.schema.CreateIndex(index)
    dialect = SQLiteDialect_pysqlite(paramstyle="named")

    # Passing `compile_kwargs` while compiling CreateIndex to a string blows up with a
    # TypeError in the SQLite dialect. I think this is just a bug in an infrequently
    # exercised corner SQLAlchemy as most of the equivalent methods in other dialects
    # accept `**kwargs`.
    with pytest.raises(
        TypeError, match="unexpected keyword argument 'render_postcompile'"
    ):
        create_index.compile(
            dialect=dialect, compile_kwargs={"render_postcompile": True}
        )

    # Check that our function compiles the query correctly
    query_str = clause_as_str(create_index, dialect)
    assert query_str == "CREATE INDEX ix_foo_bar ON foo (bar)"


def test_clause_as_str_with_expanding_bindparameter_and_bind_expression():
    # This test confirms the presence of a SQLAlchemy bug which we have to work around
    # in `clause_as_str`. If this gets fixed we want to know so that we can remove all
    # the hand-rolled parameter interpolation.

    # Create a custom type with a "bind_expression", see:
    # https://docs.sqlalchemy.org/en/14/core/type_api.html#sqlalchemy.types.TypeEngine.bind_expression
    class CustomType(sqlalchemy.types.TypeDecorator):
        impl = sqlalchemy.types.String
        cache_ok = True

        # This means that every time we reference of value of this type it gets wrapped
        # in a function call
        def bind_expression(self, bindvalue):
            return sqlalchemy.func.upper(bindvalue)

    table = sqlalchemy.Table(
        "tbl", sqlalchemy.MetaData(), sqlalchemy.Column("col", CustomType())
    )

    # With a single value comparison like `==` we can compile this to either a
    # parameterised string, or a string containing literals and it works as expected
    equality_expr = table.c.col == "abc"
    assert (
        str(equality_expr.compile(compile_kwargs={"render_postcompile": True}))
        == "tbl.col = upper(:col_1)"
    )
    assert (
        str(equality_expr.compile(compile_kwargs={"literal_binds": True}))
        == "tbl.col = upper('abc')"
    )

    # With a multi-valued comparison like `IN` we get an "expanding" BindParameter, see:
    # https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.bindparam.params.expanding
    contains_expr = table.c.col.in_(["abc", "def"])
    # We can compile this to a parameterised string and get the expected output
    assert (
        str(contains_expr.compile(compile_kwargs={"render_postcompile": True}))
        == "tbl.col IN (upper(:col_1_1), upper(:col_1_2))"
    )
    # But attempting to compile this using string literals triggers an error
    with pytest.raises(
        AttributeError, match="'NoneType' object has no attribute 'group'"
    ):
        contains_expr.compile(compile_kwargs={"literal_binds": True})

    # However our `clause_to_str` functions renders it as expected
    compiled = clause_as_str(contains_expr, DefaultDialect())
    assert compiled == "tbl.col IN (upper('abc'), upper('def'))"
