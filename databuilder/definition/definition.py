from .base import cohort_registry


def register(cohort):  # pragma: no cover (re-implement when the QL is in)
    """
    Compile a cohort's variables
    cohort: A Cohort instance
    returns: list of tuples of variable name and compiled Value
    """
    cohort_registry.add(cohort)
