import dataclasses

from databuilder.main import get_query_engine, open_output_file
from databuilder.query_engines.sqlite import SQLiteQueryEngine


@dataclasses.dataclass
class DummyQueryEngine:
    dsn: str
    backend: object
    config: dict


class DummyBackend:
    query_engine_class = DummyQueryEngine


def test_get_query_engine_defaults():
    query_engine = get_query_engine(
        dsn=None, backend_id=None, query_engine_id=None, environ={}
    )
    assert isinstance(query_engine, SQLiteQueryEngine)


def test_get_query_engine_with_query_engine():
    query_engine_id = f"{DummyQueryEngine.__module__}.{DummyQueryEngine.__name__}"
    query_engine = get_query_engine(
        dsn=None, backend_id=None, query_engine_id=query_engine_id, environ={}
    )
    assert isinstance(query_engine, DummyQueryEngine)
    assert query_engine.backend is None
    assert query_engine.config == {}


def test_get_query_engine_with_backend():
    backend_id = f"{DummyBackend.__module__}.{DummyBackend.__name__}"
    query_engine = get_query_engine(
        dsn=None, backend_id=backend_id, query_engine_id=None, environ={}
    )
    assert isinstance(query_engine, DummyQueryEngine)
    assert isinstance(query_engine.backend, DummyBackend)
    assert query_engine.config == {}


def test_get_query_engine_with_backend_and_query_engine():
    backend_id = f"{DummyBackend.__module__}.{DummyBackend.__name__}"
    query_engine_id = "databuilder.query_engines.sqlite.SQLiteQueryEngine"
    query_engine = get_query_engine(
        dsn=None, backend_id=backend_id, query_engine_id=query_engine_id, environ={}
    )
    assert isinstance(query_engine, SQLiteQueryEngine)
    assert isinstance(query_engine.backend, DummyBackend)
    assert query_engine.config == {}


def test_open_output_file(tmp_path):
    test_file = tmp_path / "testdir" / "file.txt"
    with open_output_file(test_file) as f:
        f.write("hello")
    assert test_file.read_text() == "hello"


def test_open_output_file_with_stdout(capsys):
    with open_output_file(None) as f:
        f.write("hello")
    assert capsys.readouterr().out == "hello"
