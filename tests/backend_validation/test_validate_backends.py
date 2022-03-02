from databuilder.backends.base import BaseBackend


def test_validate_all_backends():
    """
    Loops through all the backends, excluding test ones,
    and validates they meet any contract that they claim to
    """
    backends = [
        backend
        for backend in BaseBackend.__subclasses__()
        if backend.__module__.startswith("databuilder.backends.")
    ]

    for backend in backends:
        backend.validate_contracts()

    # Checks at least 3 backends
    assert len(backends) >= 3
