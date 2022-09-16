import dataclasses

from databuilder.main import get_query_engine, open_output_file
from databuilder.query_engines.csv import CSVQueryEngine


@dataclasses.dataclass
class DummyQueryEngine:
    dsn: str
    backend: object
    config: dict


class DummyBackend:
    query_engine_class = DummyQueryEngine


def test_get_query_engine_defaults():
    query_engine = get_query_engine(
        dsn=None, backend_class=None, query_engine_class=None, environ={}
    )
    assert isinstance(query_engine, CSVQueryEngine)


def test_get_query_engine_with_query_engine():
    query_engine = get_query_engine(
        dsn=None, backend_class=None, query_engine_class=DummyQueryEngine, environ={}
    )
    assert isinstance(query_engine, DummyQueryEngine)
    assert query_engine.backend is None
    assert query_engine.config == {}


def test_get_query_engine_with_backend():
    query_engine = get_query_engine(
        dsn=None, backend_class=DummyBackend, query_engine_class=None, environ={}
    )
    assert isinstance(query_engine, DummyQueryEngine)
    assert isinstance(query_engine.backend, DummyBackend)
    assert query_engine.config == {}


def test_get_query_engine_with_backend_and_query_engine():
    query_engine = get_query_engine(
        dsn=None,
        backend_class=DummyBackend,
        query_engine_class=CSVQueryEngine,
        environ={},
    )
    assert isinstance(query_engine, CSVQueryEngine)
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
