from . import query_language as ql
from .dsl import Dataset as DSLDataset


def get_class_vars(cls):
    default_vars = set(dir(type("ArbitraryEmptyClass", (), {})))
    return [(key, value) for key, value in vars(cls).items() if key not in default_vars]


def get_dataset_variables(dataset):  # pragma: no cover (re-implement when the QL is in)
    return [
        (variable_name, variable.value)
        for (variable_name, variable) in vars(dataset).items()
    ]


def get_column_definitions(dataset):
    if isinstance(dataset, ql.Dataset):
        return ql.compile(dataset)

    # This is where we distinguish between versions of the DSL
    if isinstance(
        dataset, DSLDataset
    ):  # pragma: no cover (re-implement when the QL is in)
        variables = get_dataset_variables(dataset)
    else:
        variables = get_class_vars(dataset)
    columns = {}
    ignored_names = ["measures", "BASE_INDEX_DATE"]
    for name, value in variables:
        if (
            name.startswith("_") or name in ignored_names
        ):  # pragma: no cover (Re-implement when testing with new QL)
            continue
        columns[name] = value
    if "population" not in columns:  # pragma: no cover (re-implement when the QL is in)
        raise ValueError("A Dataset definition must define a 'population' variable")
    return columns


def get_measures(dataset_cls):
    for name, value in get_class_vars(dataset_cls):
        if name == "measures":
            return value
    return []
