from .base import registered_cohorts


class Cohort:
    ...


def register(cohort):
    """
    Compile a cohort's variables
    cohort: A Cohort instance
    returns: list of tuples of variable name and compiled Value
    """
    registered_cohorts.add(cohort)


def pick_first_value(source_table):
    """
    Pick the first value by date for a single column
    source_table: query_language.Table, the table to be reduced
    returns: Row with one row per patient, sorted by date
    """
    return source_table.first_by("date")
