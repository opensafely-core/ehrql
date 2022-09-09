from databuilder import tables
from databuilder.contracts import constraints
from databuilder.module_utils import is_proper_subclass


def test_all_required_classes_are_exported():
    # If we add a new Constraint we don't want to forget to make it available via
    # `databuilder.tables`
    all_constraints = [
        cls
        for cls in vars(constraints).values()
        if is_proper_subclass(cls, constraints.BaseConstraint)
    ]
    for cls in all_constraints:
        name = cls.__name__
        assert name in tables.__all__
        assert getattr(tables, name) is cls
