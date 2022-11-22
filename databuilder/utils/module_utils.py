import importlib
import sys
from pathlib import Path


def get_sibling_subclasses(cls):
    """
    Return all subclasses of `cls` defined in modules which are siblings of the module
    containing `cls`

    For example, sibling subclasses of the class `databuilder.backends.base.BaseBackend`
    include:

        databuilder.backends.tpp.TPPBackend
        databuilder.backends.graphet.GraphnetBackend
        ...

    This is useful for tests and for generating documentation, but isn't intended for
    use in runtime code.
    """
    module_name = cls.__module__.rpartition(".")[0]
    module = sys.modules[module_name]
    return [
        obj
        for submodule in get_submodules(module)
        for obj in vars(submodule).values()
        if is_proper_subclass(obj, cls)
    ]


def get_submodules(module):
    """
    Given a module yield all its submodules recursively
    """
    submodule_names = [
        f"{module.__name__}.{f.stem}"
        for f in Path(module.__file__).parent.glob("*.py")
        if f.name != "__init__.py"
    ]
    subpackage_names = [
        f"{module.__name__}.{f.parent.name}"
        for f in Path(module.__file__).parent.glob("*/__init__.py")
    ]
    for name in submodule_names:
        yield importlib.import_module(name)
    for name in subpackage_names:
        subpackage = importlib.import_module(name)
        yield subpackage
        yield from get_submodules(subpackage)


def is_proper_subclass(value, cls):
    try:
        return issubclass(value, cls) and value is not cls
    except TypeError:
        return False
