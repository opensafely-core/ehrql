from databuilder.backends.base import BaseBackend
from databuilder.module_utils import get_sibling_subclasses


def test_validate_all_backends():
    """
    Loops through all the backends, excluding test ones,
    and validates they meet any contract that they claim to
    """
    backend_classes = get_sibling_subclasses(BaseBackend)
    for backend in backend_classes:
        backend.validate_contracts()

    # Checks at least 3 backends
    assert len(backend_classes) >= 3
