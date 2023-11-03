import pytest

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
