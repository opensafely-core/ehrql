from .base import cohort_registry


class Cohort:
    ...


def register(cohort):
    """
    Compile a cohort's variables
    cohort: A Cohort instance
    returns: list of tuples of variable name and compiled Value
    """
    cohort_registry.add(cohort)


def pick_first_value(source_table, column_name):
    """
    Pick the first value by date for a single column
    source_table: query_language.Table, the table to be reduced
    returns: Row with one row per patient, sorted by date
    """
    return source_table.first_by("date").get(column_name)


def count(source_table, column_name):
    """
    Return the query language structure that represents summing the
    values per patient for a column
    source_table: query_language.Table, the table to be reduced
    column_name: column to be counted
    returns: query_language.ValueFromAggregagte
    """
    return source_table.count(column_name)


def exists(source_table, column_name):
    """
    Return the query language structure that represents an exists query
    per patient for a column
    source_table: query_language.Table, the table to be reduced
    column_name: target column
    returns: query_language.ValueFromAggregagte
    """
    return source_table.exists(column_name)
