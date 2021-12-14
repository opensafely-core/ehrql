import sqlalchemy


def select_first_row_per_partition(query, partition_column, sort_columns, descending):
    """
    Given a SQLAlchemy SELECT query, partition it by the specified column, sort
    within each partition by `sort_columns` and then return a query containing just
    the first row for each partition.
    """
    # Get the base table - the first in the FROM clauses
    table_expr = get_primary_table(query)

    # Find all the selected column names
    column_names = [column.name for column in query.selected_columns]

    # Query to select the columns that we need to sort on
    order_columns = [table_expr.c[column] for column in sort_columns]
    # change ordering to descending on all order columns if necessary
    if descending:
        order_columns = [c.desc() for c in order_columns]

    # Number rows sequentially over the order by columns for each patient id
    row_num = (
        sqlalchemy.func.row_number()
        .over(order_by=order_columns, partition_by=table_expr.c[partition_column])
        .label("_row_num")
    )
    # Add the _row_num column and select just the first row
    query = query.add_columns(row_num)
    subquery = query.alias()
    query = sqlalchemy.select([subquery.c[column] for column in column_names])
    query = query.select_from(subquery).where(subquery.c._row_num == 1)
    return query


def group_and_aggregate(
    query, group_by_column, input_column, function_name, output_column
):
    """
    Given a SQLAlchemy SELECT query, apply the aggregation specified by `function_name`
    to `input_colum`, grouping by `group_by_column` and labelling the result as
    `output_column`
    """
    if function_name == "exists":
        aggregate_value = sqlalchemy.literal(True)
    else:
        function = getattr(sqlalchemy.func, function_name)
        source_column = query.selected_columns[input_column]
        aggregate_value = function(source_column)

    query = query.with_only_columns(
        [
            query.selected_columns[group_by_column],
            aggregate_value.label(output_column),
        ]
    )
    return query.group_by(query.selected_columns[group_by_column])


def get_joined_tables(select_query):
    """
    Given a SELECT query object return a list of all tables referenced
    """
    tables = []
    from_exprs = list(select_query.get_final_froms())
    while from_exprs:
        next_expr = from_exprs.pop()
        if isinstance(next_expr, sqlalchemy.sql.selectable.Join):
            from_exprs.extend([next_expr.left, next_expr.right])
        else:
            tables.append(next_expr)
    # The above algorithm produces tables in right to left order, but it makes
    # more sense to return them as left to right
    tables.reverse()
    return tables


def get_primary_table(select_query):
    """
    Return the left-most table referenced in the SELECT query
    """
    return get_joined_tables(select_query)[0]


def include_joined_tables(select_query, tables, join_column):
    """
    Ensure that each table in `tables` is included in the join conditions for
    `select_query`
    """
    current_tables = get_joined_tables(select_query)
    for table in tables:
        if table in current_tables:
            continue
        join = sqlalchemy.join(
            select_query.get_final_froms()[0],
            table,
            select_query.selected_columns[join_column] == table.c[join_column],
            isouter=True,
        )
        select_query = select_query.select_from(join)
        current_tables.append(table)
    return select_query


def get_referenced_tables(clause):
    """
    Given an arbitrary SQLAlchemy clause determine what tables it references
    """
    if isinstance(clause, sqlalchemy.Table):
        return (clause,)
    if hasattr(clause, "table"):
        return (clause.table,)
    else:
        tables = set()
        for child in clause.get_children():
            tables.update(get_referenced_tables(child))
        return tuple(tables)


class TemporaryTable(sqlalchemy.Table):
    """
    This wraps a standard SQLAlchemy table and adds a pair of extra attributes which are
    a list of queries needed to create and populate this table and a list of queries
    needed to clean it up.

    This means that all the setup/cleanup logic for temporary tables can be bundled up
    with the queries that use them and they no longer need to be manged out-of-band.
    """

    setup_queries = ()
    cleanup_queries = ()


def get_setup_and_cleanup_queries(clause):
    """
    Given a SQLAlchemy ClauseElement find all TemporaryTables embeded in it and return a
    pair of:

        setup_queries, cleanup_queries

    which are the combination of all the setup and cleanup queries from those
    TemporaryTables in the correct order for execution.

    There's obviously a bit of algorithmic complexity here, but it's a fairly generic,
    graph traversal kind of complexity, contained in one place, which allows us to avoid
    structural complexity elsewhere in the code so I think it's worth it.
    """
    # TemporaryTables can be arbitrarily nested in that their setup queries can
    # themselves contain references to TemporaryTables and so on. So we need to
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
    clauses = [(clause, 0, set())]
    table_levels = {}
    while clauses:
        next_clause, level, seen = clauses.pop(0)
        for table in get_temporary_tables(next_clause):
            if table in seen:
                continue
            # We may end up setting this multiple times, but if so we'll set the highest
            # level last, which is what we want
            table_levels[table] = level
            # Add all of the tables setup and cleanup queries to the stack to be checked
            clauses.extend(
                [
                    (query, level + 1, seen | {table})
                    for query in table.setup_queries + table.cleanup_queries
                ]
            )

    # Sort tables in reverse order by level
    tables = sorted(
        table_levels.keys(),
        key=table_levels.__getitem__,
        reverse=True,
    )

    setup_queries = []
    cleanup_queries = []
    for table in tables:
        setup_queries.extend(table.setup_queries)
        # Add cleanup queries to the start of the list so they end up in mirror image
        # order to the setup queries
        cleanup_queries[:0] = table.cleanup_queries

    return setup_queries, cleanup_queries


def get_temporary_tables(clause):
    """
    Return any TemporaryTable objects referenced by `clause`
    """
    return [
        table
        for table in get_referenced_tables(clause)
        if isinstance(table, TemporaryTable)
    ]
