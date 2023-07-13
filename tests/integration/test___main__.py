import contextlib
from pathlib import Path

from ehrql.__main__ import (
    BACKEND_ALIASES,
    QUERY_ENGINE_ALIASES,
    backend_from_id,
    main,
    query_engine_from_id,
)
from ehrql.backends.base import BaseBackend
from ehrql.query_engines.base import BaseQueryEngine
from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.utils.module_utils import get_sibling_subclasses


def test_assure(capsys):
    path = Path(__file__).parents[1] / "fixtures" / "assurance" / "assurance.py"
    main(["assure", str(path)])
    out, _ = capsys.readouterr()
    assert "All OK" in out


def test_test_connection(mssql_database, capsys):
    env = {
        "BACKEND": "ehrql.backends.tpp.TPPBackend",
        "DATABASE_URL": mssql_database.host_url(),
    }
    argv = ["test-connection"]
    main(argv, env)
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out


def test_dump_example_data(tmpdir):
    with contextlib.chdir(tmpdir):
        main(["dump-example-data"])
    filenames = [path.basename for path in (tmpdir / "example-data").listdir()]
    assert "patients.csv" in filenames


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
        # We don't (currently) expose the in-memory engine as an option to users
        if cls is InMemoryQueryEngine:
            continue
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in QUERY_ENGINE_ALIASES.values(), f"No alias defined for '{name}'"


def test_all_backends_have_an_alias():
    for cls in get_sibling_subclasses(BaseBackend):
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in BACKEND_ALIASES.values(), f"No alias defined for '{name}'"


def test_all_backend_aliases_match_display_names():
    for alias in BACKEND_ALIASES.keys():
        assert backend_from_id(alias).display_name.lower() == alias
