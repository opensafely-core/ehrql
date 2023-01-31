import graphlib
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
    # themselves contain references to GeneratedTables and so on. We need to
    # recursively unpack these and get them in the right order so that each query is
    # only executed after its dependencies have been executed.
    #
    # Fortunately, Python's graphlib can do most of the work for us here. We just to
    # give it a sequence of pairs of tables (A, B) indicating that A depends on B and it
    # returns a suitable ordering over the tables.
    sorter = graphlib.TopologicalSorter()
    for parent_table, table in get_generated_table_dependencies(query):
        # A parent_table of None indicates a root table (i.e. one with no dependants) so
        # we record its existence without specifying any dependencies
        if parent_table is None:
            sorter.add(table)
        # An oddity of the GeneratedTable class is that instances generally hold a
        # reference to themselves: one of the setup queries for table X will often be
        # "create a table with the structure given by X". We ignore this apparent
        # (though not actual) circularity.
        elif parent_table is table:
            pass
        # Otherwise we record the dependency between the two tables
        else:
            sorter.add(parent_table, table)

    # Tim Peters requests that you hold his beer ...
    tables = list(sorter.static_order())

    setup_queries = flatten_iter(t.setup_queries for t in tables)
    # Concatenate cleanup queries into one list, but in reverse order to that which we
    # created them in. This means that if there are any database-level dependencies
    # between the tables (e.g. if one is a materialized view over another) then we don't
    # risk errors by trying to delete objects which still have dependents.
    cleanup_queries = flatten_iter(t.cleanup_queries for t in reversed(tables))

    return setup_queries, cleanup_queries


def get_generated_table_dependencies(query, parent_table=None, seen_tables=None):
    """
    Recursively find all GeneratedTable objects referenced by `query` and yield as pairs
    of dependencies:

        table_X, table_Y_which_is_referenced_by_X

    Note that the same table may appear multiple times in this sequence.
    """
    if seen_tables is None:
        seen_tables = set()

    for table in get_generated_tables(query):
        yield parent_table, table
        # Don't recurse into the same table twice
        if table not in seen_tables:
            seen_tables.add(table)
            for child_query in [*table.setup_queries, *table.cleanup_queries]:
                yield from get_generated_table_dependencies(
                    child_query, parent_table=table, seen_tables=seen_tables
                )


def get_generated_tables(clause):
    """
    Return any GeneratedTable objects directly referenced by a SQLAlchemy ClauseElement
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
