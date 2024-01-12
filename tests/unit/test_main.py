import dataclasses
from pathlib import Path
from unittest import mock

import pytest

from ehrql.main import (
    generate_dataset,
    get_query_engine,
    open_output_file,
)


@dataclasses.dataclass
class DummyQueryEngine:
    dsn: str
    backend: object
    config: dict


@dataclasses.dataclass
class DefaultQueryEngine:
    dsn: str
    backend: object
    config: dict


@dataclasses.dataclass
class DummyBackend:
    config: dict
    query_engine_class = DummyQueryEngine


@pytest.fixture
def mock_load_and_compile():
    m = "ehrql.main"
    with mock.patch(f"{m}.load_dataset_definition", return_value=(None, None)):
        yield


def test_generate_dataset_dsn_arg(mock_load_and_compile):
    with mock.patch("ehrql.main.generate_dataset_with_dsn") as p:
        generate_dataset(
            Path("dataset_definition.py"),
            Path("results.csv"),
            # Interesting argument
            dsn="sqlite://:memory:",
            # Defaults
            backend_class=None,
            query_engine_class=None,
            dummy_tables_path=None,
            dummy_data_file=None,
            test_data_file=None,
            environ={},
            user_args=(),
        )
        p.assert_called_once()


def test_generate_dataset_dummy_data_file_arg(mock_load_and_compile):
    with mock.patch("ehrql.main.generate_dataset_with_dummy_data") as p:
        generate_dataset(
            Path("dataset_definition.py"),
            Path("results.csv"),
            # Interesting argument
            dummy_data_file="dummy-data.csv",
            # Defaults
            dsn=None,
            backend_class=None,
            query_engine_class=None,
            dummy_tables_path=None,
            test_data_file=None,
            environ={},
            user_args=(),
        )
        p.assert_called_once()


def test_generate_dataset_no_data_args(mock_load_and_compile):
    with mock.patch("ehrql.main.generate_dataset_with_dummy_data") as p:
        generate_dataset(
            Path("dataset_definition.py"),
            Path("results.csv"),
            # Defaults
            dsn=None,
            backend_class=None,
            query_engine_class=None,
            dummy_tables_path=None,
            dummy_data_file=None,
            test_data_file=None,
            environ={},
            user_args=(),
        )
        p.assert_called_once()


def test_generate_dataset_with_test_data_file(mock_load_and_compile):
    with (
        mock.patch("ehrql.main.assure") as p,
        mock.patch("ehrql.main.generate_dataset_with_dummy_data"),
    ):
        generate_dataset(
            Path("dataset_definition.py"),
            Path("results.csv"),
            # Interesting argument
            test_data_file=Path("test_data.py"),
            # Defaults
            dsn=None,
            backend_class=None,
            query_engine_class=None,
            dummy_tables_path=None,
            dummy_data_file=None,
            environ={},
            user_args=(),
        )
        p.assert_called_once()


def test_get_query_engine_defaults():
    query_engine = get_query_engine(
        dsn=None,
        backend_class=None,
        query_engine_class=None,
        environ={},
        default_query_engine_class=DefaultQueryEngine,
    )
    assert isinstance(query_engine, DefaultQueryEngine)


def test_get_query_engine_with_query_engine():
    query_engine = get_query_engine(
        dsn=None,
        backend_class=None,
        query_engine_class=DummyQueryEngine,
        environ={},
        default_query_engine_class=None,
    )
    assert isinstance(query_engine, DummyQueryEngine)
    assert query_engine.backend is None
    assert query_engine.config == {}


def test_get_query_engine_with_backend():
    query_engine = get_query_engine(
        dsn=None,
        backend_class=DummyBackend,
        query_engine_class=None,
        environ={"foo": "bar"},
        default_query_engine_class=None,
    )
    assert isinstance(query_engine, DummyQueryEngine)
    assert isinstance(query_engine.backend, DummyBackend)
    assert query_engine.config == {"foo": "bar"}
    assert query_engine.backend.config == {"foo": "bar"}


def test_get_query_engine_with_backend_and_query_engine():
    query_engine = get_query_engine(
        dsn=None,
        backend_class=DummyBackend,
        query_engine_class=DefaultQueryEngine,
        environ={},
        default_query_engine_class=None,
    )
    assert isinstance(query_engine, DefaultQueryEngine)
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
