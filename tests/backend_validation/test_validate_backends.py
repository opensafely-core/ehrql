import importlib
from pathlib import Path

from databuilder import backends
from databuilder.backends.base import BaseBackend


def test_validate_all_backends():
    """
    Loops through all the backends, excluding test ones,
    and validates they meet any contract that they claim to
    """
    # Import all modules inside `databuilder.backends`
    module_names = [f.stem for f in Path(backends.__file__).parent.glob("*.py")]
    for module_name in module_names:
        importlib.import_module(f"{backends.__name__}.{module_name}")

    backend_classes = [
        backend
        for backend in BaseBackend.__subclasses__()
        if backend.__module__.startswith("databuilder.backends.")
    ]

    for backend in backend_classes:
        backend.validate_contracts()

    # Checks at least 3 backends
    assert len(backend_classes) >= 3
