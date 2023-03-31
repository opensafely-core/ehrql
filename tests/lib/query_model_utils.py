import dataclasses

from databuilder.query_model import nodes as query_model


# These are only exercised during the long-running generative tests when
# GENTEST_COMPREHENSIVE is enabled


def get_all_operations():  # pragma: no cover
    "Return every operation defined in the query model"
    return [cls for cls in iterate_query_model_namespace() if is_operation(cls)]


def is_operation(cls):  # pragma: no cover
    "Return whether an arbitrary value is a query model operation class"
    # We need to check this first or the `issubclass` check can fail
    if not isinstance(cls, type):
        return False
    # We need to check it's a proper subclass as the Node base class isn't itself a
    # dataclass so the `fields()` call will fail
    if not issubclass(cls, query_model.Node) or cls is query_model.Node:
        return False
    # If it takes arguments it's an operation, otherwise it's an abstract type
    return len(dataclasses.fields(cls)) > 0


def iterate_query_model_namespace():  # pragma: no cover
    "Yield every value in the query_model module"
    yield from vars(query_model).values()
    yield from vars(query_model.Function).values()
    yield from vars(query_model.AggregateByPatient).values()
