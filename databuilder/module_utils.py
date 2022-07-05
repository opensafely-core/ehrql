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
    module_file = sys.modules[cls.__module__].__file__
    module_names = [f.stem for f in Path(module_file).parent.glob("*.py")]
    package = cls.__module__.rpartition(".")[0]
    for module_name in module_names:
        importlib.import_module(f"{package}.{module_name}")
    return [
        subclass
        for subclass in cls.__subclasses__()
        if subclass.__module__.startswith(f"{package}.")
    ]
