from sqlalchemy.sql.elements import AsBoolean, BinaryExpression, BooleanClauseList


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
    return False
