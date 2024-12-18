import pytest
from trino import exceptions as trino_exceptions

from ehrql.backends.emis import EMISBackend


@pytest.mark.parametrize(
    "exception",
    [
        # These are trino errors that we may want to support in future with
        # custom exit codes, but currently inherit from the base method
        # Database errors
        trino_exceptions.DatabaseError,
        # OperationError is a subclass of DatabaseError
        trino_exceptions.OperationalError,
        # TrinoQueryError is encountered for over-complex/over-nested queries
        trino_exceptions.TrinoQueryError,
        # TrinoUserError is encountered for out of range numbers
        trino_exceptions.TrinoUserError,
        # TrinoUserError is encountered for bad/out of range dates
        trino_exceptions.TrinoDataError,
    ],
)
def test_backend_exceptions(exception):
    backend = EMISBackend()
    assert backend.get_exit_status_for_exception(exception) is None
