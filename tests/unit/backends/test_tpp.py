import pytest
from pymssql import exceptions as pymssql_exceptions

from ehrql.backends.tpp import TPPBackend


@pytest.mark.parametrize(
    "dsn_in,dsn_out,t1oo_status",
    [
        (
            "mssql://user:pass@localhost:4321/db",
            "mssql://user:pass@localhost:4321/db",
            False,
        ),
        (
            "mssql://user:pass@localhost:4321/db?param1=one&param2&param1=three",
            "mssql://user:pass@localhost:4321/db?param1=one&param1=three&param2=",
            False,
        ),
        (
            "mssql://user:pass@localhost:4321/db?opensafely_include_t1oo&param2=two",
            "mssql://user:pass@localhost:4321/db?param2=two",
            False,
        ),
        (
            "mssql://user:pass@localhost:4321/db?opensafely_include_t1oo=false",
            "mssql://user:pass@localhost:4321/db",
            False,
        ),
        (
            "mssql://user:pass@localhost:4321/db?opensafely_include_t1oo=true",
            "mssql://user:pass@localhost:4321/db",
            True,
        ),
        (
            "mssql://user:pass@localhost:4321/db?opensafely_include_t1oo=True",
            "mssql://user:pass@localhost:4321/db",
            True,
        ),
    ],
)
def test_tpp_backend_modify_dsn(dsn_in, dsn_out, t1oo_status):
    backend = TPPBackend()
    assert backend.modify_dsn(dsn_in) == dsn_out
    assert backend.include_t1oo == t1oo_status


@pytest.mark.parametrize(
    "dsn",
    [
        "mssql://user:pass@localhost:4321/db?opensafely_include_t1oo=false&opensafely_include_t1oo=false",
        "mssql://user:pass@localhost:4321/db?opensafely_include_t1oo=false&opensafely_include_t1oo",
    ],
)
def test_tpp_backend_modify_dsn_rejects_duplicate_params(dsn):
    backend = TPPBackend()
    with pytest.raises(ValueError, match="must not be supplied more than once"):
        backend.modify_dsn(dsn)


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
def test_backend_exceptions(exception, exit_code, custom_err):
    backend = TPPBackend()
    assert backend.get_exit_status_for_exception(exception) == exit_code

    if custom_err is not None:  # pragma: no cover
        assert any(custom_err in note for note in exception.__notes__)
