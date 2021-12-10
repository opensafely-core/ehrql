import sqlalchemy


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
