from .query_language import Value


def get_class_vars(cls):
    default_vars = set(dir(type("ArbitraryEmptyClass", (), {})))
    return [(key, value) for key, value in vars(cls).items() if key not in default_vars]


def get_column_definitions(cohort_cls):
    columns = {}
    ignored_names = ["measures", "BASE_INDEX_DATE"]
    for name, value in get_class_vars(cohort_cls):
        if name.startswith("_") or name in ignored_names:
            continue
        if not isinstance(value, Value):
            raise ValueError(f"Cohort variable '{name}' is not a Value")
        columns[name] = value
    return columns


def get_measures(cohort_cls):
    for name, value in get_class_vars(cohort_cls):
        if name == "measures":
            return value
