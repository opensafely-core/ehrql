from ..query_interface import Variable
from .base import cohort_registry


class Cohort:
    """Represents the cohort of patients in a study."""

    population = NotImplemented

    def set_population(self, population: Variable) -> None:
        """Set the population variable for this cohort."""
        self.add_variable("population", population)
        if not self.population.reduce_function.__name__ == "exists":
            raise ValueError(
                "Population variable must return a boolean. Did you mean to use `make_one_row_per_patient(exists)`?"
            )

    def add_variable(self, name: str, variable: Variable) -> None:
        """Add a variable to this cohort by name."""
        if not isinstance(variable, Variable):
            raise TypeError(
                f"{name} must be a single value per patient (got '{variable.__class__.__name__}')"
            )
        self.__dict__[name] = variable

    def __setattr__(self, name: str, variable: Variable) -> None:
        return self.add_variable(name, variable)


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
