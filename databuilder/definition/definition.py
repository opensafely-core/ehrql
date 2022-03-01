from .base import dataset_registry


def register(dataset):  # pragma: no cover (re-implement when the QL is in)
    """
    Compile a dataset's variables
    dataset: A Dataset instance
    returns: list of tuples of variable name and compiled Value
    """
    dataset_registry.add(dataset)
