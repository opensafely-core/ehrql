from .base import cohort_registry


def register(cohort):
    """
    Compile a cohort's variables
    cohort: A Cohort instance
    returns: list of tuples of variable name and compiled Value
    """
    cohort_registry.add(cohort)
