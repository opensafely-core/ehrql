import re

import sqlalchemy
from sqlalchemy.sql.elements import (
    AsBoolean,
    BinaryExpression,
    BooleanClauseList,
    UnaryExpression,
    operators,
)
from sqlalchemy.sql.visitors import iterate


def is_predicate(clause):
    """
    Some boolean expressions are guaranteed to be boolean-typed by virtue of their
    syntax, e.g.

      a == b

    Others happen to be boolean-typed by virtue of the columns they use, but you can't
    tell just by looking at them, e.g.

      some_table.some_boolean_column

    We call the former class "predicates".

    While some databases treat both classes of boolean expression as equivalent, others
    have rules about which syntactic contexts accept predicates and which accept boolean
    expressions. As the two are semantically equivalent we can always convert from one
    to other, but we need to know which is which so we can apply the appropriate
    conversion rules.
    """
    if isinstance(clause, (BooleanClauseList, AsBoolean)):
        return True
    if isinstance(clause, BinaryExpression):
        return clause._is_implicitly_boolean
    # We have to identify `NOT ...` expressions by the operator they use
    if isinstance(clause, UnaryExpression) and clause.operator is operators.inv:
        return True
    return False


class GeneratedTable(sqlalchemy.Table):
    """
    This wraps a standard SQLAlchemy Table and adds a pair of extra attributes
    which are a sequence of queries needed to create and populate this table and a
    sequence (possibly empty) of queries needed to clean it up.

    This provides a generic mechanism for constructing "multi-step" queries i.e. queries
    that require creating intermediate objects before fetching their results. These
    intermediate objects could be temporary tables, persistent tables, views, or
    anything else so long as it functions syntactically as a table.
    """

    setup_queries = ()
    cleanup_queries = ()


def get_setup_and_cleanup_queries(query):
    """
    Given a SQLAlchemy query find all GeneratedTables embeded in it and return a pair:

        setup_queries, cleanup_queries

    which are the combination of all the setup and cleanup queries from those
    GeneratedTables in the correct order for execution.
    """
    # GeneratedTables can be arbitrarily nested in that their setup queries can
    # themselves contain references to GeneratedTables and so on. So we need to
    # recursively unpack these, taking note of a number of subtleties:
    #
    #  1. We need to keep track of what level of nesting each table is at. The setup
    #     queries for the most deeply nested tables must be run first so they exist by
    #     the time queries for their dependant tables get run.
    #
    #  2. The same table can occur at multiple levels of nesting so we need to track the
    #     highest level for each table.
    #
    #  3. By construction there can be no cycles in this graph *except* that each
    #     table's setup queries will contain a reference to itself (as part of a "create
    #     this table" statement). This means we need to keep track of which tables we've
    #     seen on each given branch to avoid looping.
    #
    queries = [(query, 0, set())]
    table_levels = {}
    while queries:
        next_query, level, seen = queries.pop(0)
        for table in get_generated_tables(next_query):
            if table in seen:
                continue
            # We may end up setting this multiple times, but if so we'll set the highest
            # level last, which is what we want
            table_levels[table] = level
            # Add all of the table's setup and cleanup queries to the stack to be checked
            queries.extend(
                (query, level + 1, seen | {table})
                for query in [*table.setup_queries, *table.cleanup_queries]
            )

    # Sort tables in reverse order by level
    tables = sorted(
        table_levels.keys(),
        key=table_levels.__getitem__,
        reverse=True,
    )

    setup_queries = flatten_iter(t.setup_queries for t in tables)
    # Concatenate cleanup queries into one list, but in reverse order to that which we
    # created them in. This means that if there are any database-level dependencies
    # between the tables (e.g. if one is a materialized view over another) then we don't
    # risk errors by trying to delete objects which still have dependents.
    cleanup_queries = flatten_iter(t.cleanup_queries for t in reversed(tables))

    return setup_queries, cleanup_queries


def get_generated_tables(clause):
    """
    Return any GeneratedTable objects referenced by a SQLAlchemy ClauseElement
    """
    return [elem for elem in iterate(clause) if isinstance(elem, GeneratedTable)]


def flatten_iter(nested_iters):
    return [i for sub_iter in nested_iters for i in sub_iter]


def clause_as_str(clause, dialect):
    """
    Return a SQL clause as a string in the supplied SQL dialect with any included
    parameters interpolated in
    """
    # Workaround: we call `.compile()` twice below, first without the `compile_kwargs`
    # argument and then again with it if the clause has bound parameters. This ought to
    # be unnecessary as compilers for clauses which don't take bound parameters should
    # accept and ignore `compile_kwargs` — and most do. But some (`visit_create_index`
    # in the SQLite dialect for example) blow up if given `compile_kwargs` so we have to
    # take this two-step approach. For more detail see:
    #   tests/unit/utils/test_sqlalchemy_query_utils.py
    #     ::test_clause_as_str_with_create_index_on_sqlite
    compiled = clause.compile(dialect=dialect)
    if not compiled.params:
        return str(compiled).strip()

    compiled = clause.compile(
        dialect=dialect,
        # `render_postcompile` is needed for handling multi-valued parameters e.g. those
        # used in the expression `some_column.in_([1, 2, 3])`. For more detail see:
        # https://docs.sqlalchemy.org/en/14/faq/sqlexpressions.html#rendering-postcompile-parameters-as-bound-parameters
        compile_kwargs={"render_postcompile": True},
    )

    # To produce a SQL expression with string literals instead of parameter placeholders
    # we compile it with placeholders, format all the parameters as string literals and
    # then substitute them in to the placeholders using a regex. In theory SQLAlchemy can
    # do this for us if we pass `"literal_binds": True` in `compile_kwargs` but sadly
    # this doesn't work in all cases. For more detail see:
    #   tests/unit/utils/test_sqlalchemy_query_utils.py
    #     ::test_clause_as_str_with_expanding_bindparameter_and_bind_expression
    compiled_str = str(compiled).strip()
    literal_params = dict(yield_params_as_literals(compiled, dialect))

    # If we need to use a dialect which uses a different parameter style then we'll have
    # to come up with an appropriate regex for it
    assert dialect.paramstyle == "named"
    return re.sub(
        # Match placeholders like ":param_1", but ignore double colons which act as
        # escape characters
        r"(?<!:):([A-Za-z_]\w*)",
        lambda m: literal_params[m.group(1)],
        compiled_str,
    )


def yield_params_as_literals(compiled, dialect):
    for key, value in compiled.params.items():
        # Get the type of the BindParameter object corresponding to each param
        param_type = compiled.binds[key].type
        # Get the implemention of this type for the supplied dialect
        dialect_impl = param_type.dialect_impl(dialect)
        # Get the processor which turns values of this type into string literals
        literal_processor = dialect_impl.literal_processor(dialect)
        # Yield the string literal with its key
        yield key, literal_processor(value)
