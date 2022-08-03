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
    # This is an awkward workaround for the fact that some constructs, e.g. CreateIndex,
    # blow up if you try to compile them with `literal_binds = True` because they don't
    # accept the `literal_binds` keyword. I _think_ this is just a bug in SQLAlchemy,
    # but one that hasn't be noticed because index definitions don't tend to take
    # paramters. In any case, the workaround here is that we compile a parameterised
    # version of the query first, and then recompile with `literal_binds` only if it
    # actually has parameters.
    compiled = clause.compile(dialect=dialect)
    if not compiled.params:
        return str(compiled).strip()
    else:
        compiled = clause.compile(
            dialect=dialect, compile_kwargs={"literal_binds": True}
        )
        return str(compiled).strip()


def fetch_table_in_batches(
    connection, table, key_column, batch_size=32000, log=lambda *_: None
):
    """
    Returns an iterator over all the rows in a table by querying it in batches

    Args:
        connection: SQLAlchemy Connection object
        table: SQLAlchemy TableClause
        key_column: reference to a unique orderable column on `table`, used for
            paging (note that this will need an index on it to avoid terrible
            performance)
        batch_size: how many results to fetch in each batch
        log: callback to receive log messages
    """
    batch_count = 1
    total_rows = 0
    min_key = None

    key_column_index = table.columns.values().index(key_column)

    log(f"Fetching rows from '{table}' in batches of {batch_size}")
    while True:
        query = sqlalchemy.select(table).order_by(key_column).limit(batch_size)
        if min_key is not None:
            query = query.where(key_column > min_key)

        log(f"Fetching batch {batch_count}")
        results = connection.execute(query)

        row_count = 0
        for row in results:
            row_count += 1
            yield row

        total_rows += row_count
        batch_count += 1

        if row_count < batch_size:
            log(f"Fetch complete, total rows: {total_rows}")
            break
        else:
            min_key = row[key_column_index]
