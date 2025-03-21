def truediv(lhs, rhs):
    """
    Implement Python truediv behaviour but return None when dividing by zero.
    """
    if rhs == 0:
        return None
    else:
        return lhs / rhs


def floordiv(lhs, rhs):
    """
    Implement Python floordiv behaviour but return None when dividing by zero.
    """
    if rhs == 0:
        return None
    else:
        return int(lhs // rhs)


def get_grouping_level_as_int(all_groups, group_subset):
    # Calculate the level of grouping for a subset of group by groups in the
    # same way as the grouping ID in sqlserver is calculated - i.e. integer representation of a string of
    # 0s and 1s for each column, where a 1 indicates that the column is NOT a grouping column
    # https://learn.microsoft.com/en-us/)sql/t-sql/functions/grouping-id-transact-sql?view=sql-server-ver16
    if not all_groups:
        return 0
    return int(
        "".join(["0" if group in group_subset else "1" for group in all_groups]),
        2,
    )
