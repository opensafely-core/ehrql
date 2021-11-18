from .definition import Cohort as CohortConcept
from .query_interface import Variable
from .query_language import Value


def get_class_vars(cls):
    default_vars = set(dir(type("ArbitraryEmptyClass", (), {})))
    return [(key, value) for key, value in vars(cls).items() if key not in default_vars]


def get_cohort_variables(cohort):
    return [
        (variable_name, variable.compile_to_query_language())
        for (variable_name, variable) in vars(cohort).items()
        if isinstance(variable, Variable)
    ]


def get_column_definitions(cohort):
    if isinstance(cohort, CohortConcept):
        variables = get_cohort_variables(cohort)
    else:
        variables = get_class_vars(cohort)
    columns = {}
    ignored_names = ["measures", "BASE_INDEX_DATE"]
    for name, value in variables:
        if name.startswith("_") or name in ignored_names:
            continue
        if not isinstance(value, Value):
            raise TypeError(
                f"Cohort variable '{name}' is not a Value (type='{type(value).__name__}')"
            )
        columns[name] = value
    if "population" not in columns:
        raise ValueError("A Cohort definition must define a 'population' variable")
    return columns


def get_measures(cohort_cls):
    for name, value in get_class_vars(cohort_cls):
        if name == "measures":
            return value
    return []
