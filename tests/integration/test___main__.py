from databuilder.__main__ import (
    BACKEND_ALIASES,
    QUERY_ENGINE_ALIASES,
    backend_from_id,
    main,
    query_engine_from_id,
)
from databuilder.backends.base import BaseBackend
from databuilder.module_utils import get_sibling_subclasses
from databuilder.query_engines.base import BaseQueryEngine
from databuilder.query_engines.base_sql import BaseSQLQueryEngine


def test_test_connection(mssql_database, capsys):
    env = {
        "BACKEND": "databuilder.backends.tpp.TPPBackend",
        "DATABASE_URL": mssql_database.host_url(),
    }
    argv = ["test-connection"]
    main(argv, env)
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out


def test_all_query_engine_aliases_are_importable():
    for alias in QUERY_ENGINE_ALIASES.keys():
        assert query_engine_from_id(alias)


def test_all_backend_aliases_are_importable():
    for alias in BACKEND_ALIASES.keys():
        assert backend_from_id(alias)


def test_all_query_engines_have_an_alias():
    for cls in get_sibling_subclasses(BaseQueryEngine):
        # Ignore abstract classes that shouldn't have an alias
        if cls is BaseSQLQueryEngine:
            continue
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in QUERY_ENGINE_ALIASES.values(), f"No alias defined for {cls}"


def test_all_backends_have_an_alias():
    for cls in get_sibling_subclasses(BaseBackend):
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in BACKEND_ALIASES.values(), f"No alias defined for {cls}"
