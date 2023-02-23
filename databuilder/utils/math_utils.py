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
