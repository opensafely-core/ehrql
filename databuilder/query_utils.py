from .dsl import Cohort as DSLCohort
from .query_model_convert_to_new import convert as convert_to_new
from .query_model_old import QueryNode as OldQueryNode


def get_class_vars(cls):
    default_vars = set(dir(type("ArbitraryEmptyClass", (), {})))
    return [(key, value) for key, value in vars(cls).items() if key not in default_vars]


def get_cohort_variables(cohort):
    return [
        (variable_name, variable.value)
        for (variable_name, variable) in vars(cohort).items()
    ]


def get_column_definitions(cohort):
    # This is where we distinguish between versions of the DSL
    if isinstance(cohort, DSLCohort):
        variables = get_cohort_variables(cohort)
    else:
        variables = get_class_vars(cohort)
    columns = {}
    ignored_names = ["measures", "BASE_INDEX_DATE"]
    for name, value in variables:
        if name.startswith("_") or name in ignored_names:
            continue
        columns[name] = value
    if "population" not in columns:
        raise ValueError("A Cohort definition must define a 'population' variable")
    # Temporary migration code: if we've been given an instance of the old Query Model
    # then convert it to the new one
    first_definition = list(columns.values())[0]
    if isinstance(first_definition, OldQueryNode):
        columns = convert_to_new(columns)
    return columns


def get_measures(cohort_cls):
    for name, value in get_class_vars(cohort_cls):
        if name == "measures":
            return value
    return []
