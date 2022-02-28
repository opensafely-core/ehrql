import inspect

from databuilder.contracts import constraints


def test_constraints_have_descriptions(subtests):
    constraint_classes = inspect.getmembers(constraints, inspect.isclass)
    constraint_classes = [
        cls for name, cls in constraint_classes if cls != constraints.BaseConstraint
    ]

    for constraint in constraint_classes:
        with subtests.test(name=constraint.__name__):
            assert hasattr(constraint(), "description")
