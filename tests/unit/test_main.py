import dataclasses
from pathlib import Path
from unittest import mock

import pytest

from ehrql.main import (
    CommandError,
    generate_dataset,
    get_query_engine,
    load_dataset_definition,
    load_measure_definitions,
    open_output_file,
)


FIXTURES = Path(__file__).parents[1] / "fixtures" / "bad_dataset_definitions"


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
    with mock.patch(f"{m}.load_dataset_definition"), mock.patch(f"{m}.compile"):
        yield


def test_generate_dataset_dsn_arg(mock_load_and_compile):
    with mock.patch("ehrql.main.generate_dataset_with_dsn") as p:
        generate_dataset(
            Path("dataset_definition.py"),
            Path("results.csv"),
            dsn="sqlite://:memory:",
            backend_class=DummyBackend,
            query_engine_class=DummyQueryEngine,
            environ={"FOO": "bar"},
        )
        p.assert_called_once()


def test_generate_dataset_dummy_data_file_arg(mock_load_and_compile):
    with mock.patch("ehrql.main.generate_dataset_with_dummy_data") as p:
        generate_dataset(
            Path("dataset_definition.py"),
            Path("results.csv"),
            dummy_data_file="dummy-data.csv",
        )
        p.assert_called_once()


def test_generate_dataset_no_data_args(mock_load_and_compile):
    with mock.patch("ehrql.main.generate_dataset_with_dummy_data") as p:
        generate_dataset(Path("dataset_definition.py"), Path("results.csv"))
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


def test_load_dataset_definition_no_dataset():
    filename = FIXTURES / "no_dataset.py"
    with pytest.raises(CommandError, match="Did not find a variable called 'dataset'"):
        load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_not_a_dataset():
    filename = FIXTURES / "not_a_dataset.py"
    with pytest.raises(
        CommandError, match=r"'dataset' must be an instance of .*\.Dataset"
    ):
        load_dataset_definition(filename, user_args=())


def test_load_dataset_definition_no_population():
    filename = FIXTURES / "no_population.py"
    with pytest.raises(CommandError, match="A population has not been defined"):
        load_dataset_definition(filename, user_args=())


def test_load_measure_definitions_no_measures():
    filename = FIXTURES / "no_measures.py"
    with pytest.raises(CommandError, match="Did not find a variable called 'measures'"):
        load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_not_measures_instance():
    filename = FIXTURES / "not_measures_instance.py"
    with pytest.raises(
        CommandError, match=r"'measures' must be an instance of .*\.Measures"
    ):
        load_measure_definitions(filename, user_args=())


def test_load_measure_definitions_empty_measures():
    filename = FIXTURES / "empty_measures.py"
    with pytest.raises(CommandError, match="No measures defined"):
        load_measure_definitions(filename, user_args=())
