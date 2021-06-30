def get_class_vars(cls):
    default_vars = set(dir(type("ArbitraryEmptyClass", (), {})))
    return [(key, value) for key, value in vars(cls).items() if key not in default_vars]


def get_column_definitions(cohort_cls):
    return {
        key: value
        for key, value in get_class_vars(cohort_cls)
        if not key.startswith("_")
    }
