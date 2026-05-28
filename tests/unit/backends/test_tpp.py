import pytest
from pymssql import exceptions as pymssql_exceptions

from ehrql.backends.tpp import TPPBackend


@pytest.mark.parametrize(
    "exception,exit_code,custom_err",
    [
        (
            pymssql_exceptions.OperationalError("Unexpected EOF from the server"),
            3,
            "Intermittent database error",
        ),
        (
            pymssql_exceptions.OperationalError("DBPROCESS is dead or not enabled"),
            3,
            "Intermittent database error",
        ),
        (
            pymssql_exceptions.OperationalError(
                "Invalid object name 'CodedEvent_SNOMED'"
            ),
            4,
            "CodedEvent_SNOMED table is currently not available",
        ),
        (
            pymssql_exceptions.OperationalError(
                "The query processor ran out of stack space"
            ),
            6,
            "Over-complex SQL error",
        ),
        (
            pymssql_exceptions.OperationalError(
                "column 'foo' in table 'bar' exceeds the maximum of 1024 columns"
            ),
            6,
            "Over-complex SQL error",
        ),
        (
            pymssql_exceptions.DataError("Database data error"),
            5,
            "Database error",
        ),
        (
            pymssql_exceptions.InternalError("Other database internal error"),
            5,
            "Database error",
        ),
        (
            pymssql_exceptions.DatabaseError("A plain old database error"),
            5,
            "Database error",
        ),
        (
            Exception("Other non-database error exception"),
            None,
            None,
        ),
    ],
)
@pytest.mark.parametrize("nested", [False, True])
def test_backend_exceptions(nested, exception, exit_code, custom_err):
    if nested:
        exception = make_nested_exception(exception)
    backend = TPPBackend()
    assert backend.get_exit_code_for_exception(exception) == exit_code

    if custom_err is not None:  # pragma: no cover
        assert any(custom_err in note for note in exception.__notes__)


class SomeOtherException(Exception): ...


def make_nested_exception(exception):
    try:
        try:
            raise exception
        except Exception:
            raise SomeOtherException()
    except Exception as new_exception:
        return new_exception
