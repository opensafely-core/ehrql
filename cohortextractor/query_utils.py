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


def get_column_definitions(cohort_class):
    if isinstance(cohort_class, CohortConcept):
        variables = get_cohort_variables(cohort_class)
    else:
        variables = get_class_vars(cohort_class)
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
    return columns


def get_measures(cohort_cls):
    return next(
        (value for name, value in get_class_vars(cohort_cls) if name == "measures"),
        [],
    )
