from pathlib import Path

import pytest

from ehrql.__main__ import (
    BACKEND_ALIASES,
    QUERY_ENGINE_ALIASES,
    ArgumentTypeError,
    backend_from_id,
    import_string,
    main,
    query_engine_from_id,
    valid_output_path,
)
from ehrql.backends.base import BaseBackend, SQLBackend
from ehrql.exceptions import (
    DefinitionError,
    FileValidationError,
)
from ehrql.measures import MeasuresTimeout
from ehrql.query_engines.base import BaseQueryEngine
from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.query_engines.debug import DebugQueryEngine
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.utils.module_utils import get_sibling_subclasses


# We just need any old existing file with a ".py" extension for testing purposes, its
# contents are immaterial; this one will do
DATASET_DEFINITON_PATH = __file__


def test_no_args(capsys):
    # Verify that when ehrql is called without arguments, help text is shown.
    with pytest.raises(SystemExit):
        main([])
    captured = capsys.readouterr()
    assert "usage: ehrql" in captured.out


def test_generate_dataset(mocker):
    # Verify that the generate_dataset subcommand can be invoked.
    patched = mocker.patch("ehrql.__main__.generate_dataset")
    argv = [
        "generate-dataset",
        DATASET_DEFINITON_PATH,
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_dataset_rejects_unknown_extension(capsys):
    argv = [
        "generate-dataset",
        DATASET_DEFINITON_PATH,
        "--output",
        "out_file.badformat",
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert ".badformat' is not a supported format" in captured.err


def test_generate_dataset_with_definition_error(capsys, mocker):
    # Verify that the generate_dataset subcommand can be invoked.
    patched = mocker.patch("ehrql.__main__.generate_dataset")
    patched.side_effect = DefinitionError("Not a good dataset definition")
    argv = [
        "generate-dataset",
        DATASET_DEFINITON_PATH,
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "Not a good dataset definition" in captured.err
    assert "Traceback" not in captured.err


def test_generate_dataset_with_validation_error(capsys, mocker):
    # Verify that the generate_dataset subcommand can be invoked.
    patched = mocker.patch("ehrql.__main__.generate_dataset")
    patched.side_effect = FileValidationError("Your file was bad")
    argv = [
        "generate-dataset",
        DATASET_DEFINITON_PATH,
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "Your file was bad" in captured.err
    assert "Traceback" not in captured.err


def test_dump_dataset_sql(mocker):
    # Verify that the dump_dataset_sql subcommand can be invoked.
    patched = mocker.patch("ehrql.__main__.dump_dataset_sql")
    argv = [
        "dump-dataset-sql",
        "--backend",
        "ehrql.backends.tpp.TPPBackend",
        DATASET_DEFINITON_PATH,
    ]
    main(argv)
    patched.assert_called_once()


@pytest.mark.parametrize("output_path", ["dummy_data_path", "dummy_data_path:arrow"])
def test_create_dummy_tables(mocker, output_path):
    # Verify that the create_dummy_tables subcommand can be invoked.
    patched = mocker.patch("ehrql.__main__.create_dummy_tables")
    argv = [
        "create-dummy-tables",
        DATASET_DEFINITON_PATH,
        output_path,
    ]
    main(argv)
    patched.assert_called_once()


def test_create_dummy_tables_rejects_unsupported_format(capsys):
    argv = [
        "create-dummy-tables",
        DATASET_DEFINITON_PATH,
        "dummy_data_path:invalid",
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "':invalid' is not a supported format" in captured.err


def test_generate_measures(mocker):
    # Verify that the generate_measures subcommand can be invoked.
    patched = mocker.patch("ehrql.__main__.generate_measures")
    argv = [
        "generate-measures",
        DATASET_DEFINITON_PATH,
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_measures_with_timeout(capsys, mocker):
    patched = mocker.patch("ehrql.__main__.generate_measures")
    patched.side_effect = MeasuresTimeout("Too slow")
    argv = [
        "generate-measures",
        DATASET_DEFINITON_PATH,
    ]
    with pytest.raises(SystemExit) as exc:
        main(argv)
    captured = capsys.readouterr()
    assert "Too slow" in captured.err
    assert "Traceback" not in captured.err
    assert exc.value.code == 14


def test_existing_python_file_missing_file(capsys, tmp_path):
    # Verify that a helpful message is shown when a command is invoked with a path to a
    # file that should exist but doesn't.
    dataset_definition_path = tmp_path / "dataset.py"
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "dataset.py does not exist" in captured.err


def test_existing_python_file_unpythonic_file(capsys, tmp_path):
    # Verify that a helpful message is shown when a command is invoked with a path to a
    # file that should be a Python file but isn't.
    dataset_definition_path = tmp_path / "dataset.cpp"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "dataset.cpp is not a Python file" in captured.err


def test_existing_directory_missing_directory(capsys, tmp_path):
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
        "--dummy-tables",
        "non-existent-directory",
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "non-existent-directory does not exist" in captured.err


def test_existing_directory_not_a_directory(capsys, tmp_path):
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    file_path = tmp_path / "not-a-directory.file"
    file_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
        "--dummy-tables",
        str(file_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "not-a-directory.file is not a directory" in captured.err


def test_valid_input_path_missing_file(capsys, tmp_path):
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
        "--dummy-data-file",
        "non-existent-file",
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "non-existent-file does not exist" in captured.err


def test_import_string():
    assert import_string("ehrql.__main__.main") is main


def test_import_string_not_a_dotted_path():
    with pytest.raises(ArgumentTypeError, match="must be a full dotted path"):
        import_string("urllib")


def test_import_string_no_such_module():
    with pytest.raises(ArgumentTypeError, match="could not import module"):
        import_string("urllib.this_is_not_a_module.Foo")


def test_import_string_no_such_attribute():
    with pytest.raises(ArgumentTypeError, match="'urllib.parse' has no attribute"):
        import_string("urllib.parse.ThisIsNotAClass")


class DummyQueryEngine:
    def get_results_tables(self):
        raise NotImplementedError()


def test_query_engine_from_id():
    engine_id = f"{DummyQueryEngine.__module__}.{DummyQueryEngine.__name__}"
    assert query_engine_from_id(engine_id) is DummyQueryEngine


def test_query_engine_from_id_missing_alias():
    with pytest.raises(ArgumentTypeError, match="must be one of"):
        query_engine_from_id("missing")


def test_query_engine_from_id_wrong_type():
    with pytest.raises(ArgumentTypeError, match="is not a valid query engine"):
        query_engine_from_id("pathlib.Path")


class DummyBackend(BaseBackend):
    def get_table_definition(self):
        raise NotImplementedError()


def test_backend_from_id():
    engine_id = f"{DummyBackend.__module__}.{DummyBackend.__name__}"
    assert backend_from_id(engine_id) is DummyBackend


def test_backend_from_id_missing_alias():
    with pytest.raises(ArgumentTypeError, match="must be one of"):
        backend_from_id("missing")


def test_backend_from_id_wrong_type():
    with pytest.raises(ArgumentTypeError, match="is not a valid backend"):
        backend_from_id("pathlib.Path")


@pytest.mark.parametrize("alias", ["expectations", "test"])
def test_backend_from_id_special_case_aliases(alias):
    assert backend_from_id(alias) is None


def test_all_query_engine_aliases_are_importable():
    for alias in QUERY_ENGINE_ALIASES.keys():
        assert query_engine_from_id(alias)


def test_all_backend_aliases_are_importable():
    for alias in BACKEND_ALIASES.keys():
        assert backend_from_id(alias)


def test_all_query_engines_have_an_alias():
    for cls in get_sibling_subclasses(BaseQueryEngine):
        if cls in [
            BaseSQLQueryEngine,
            InMemoryQueryEngine,
            DebugQueryEngine,
        ]:
            continue
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in QUERY_ENGINE_ALIASES.values(), f"No alias defined for '{name}'"


def test_all_backends_have_an_alias():
    for cls in get_sibling_subclasses(SQLBackend):
        name = f"{cls.__module__}.{cls.__name__}"
        assert name in BACKEND_ALIASES.values(), f"No alias defined for '{name}'"


def test_all_backend_aliases_match_display_names():
    for alias in BACKEND_ALIASES.keys():
        assert backend_from_id(alias).display_name.lower() == alias


@pytest.mark.parametrize(
    "path",
    [
        "some/path/file.csv",
        "some/path/dir:csv",
        "some/path/dir/:csv",
        "some/path/dir.foo:csv",
    ],
)
def test_valid_output_path(path):
    assert valid_output_path(path) == Path(path)


@pytest.mark.parametrize(
    "path, message",
    [
        ("no/extension", "No file format specified"),
        ("some/path.badfile", "'.badfile' is not a supported format"),
        ("some/path:baddir", "':baddir' is not a supported format"),
        ("some/path/:baddir", "':baddir' is not a supported format"),
    ],
)
def test_valid_output_path_errors(path, message):
    with pytest.raises(ArgumentTypeError, match=message):
        valid_output_path(path)


# Helpers for backend-admin tests


class CaptureTask:
    """
    Task module shaped object that records the kwargs passed to `run()` so
    tests can assert on what dispatch handed in.
    """

    HELP = "A fake task for testing."
    captured: dict = {}

    @staticmethod
    def add_arguments(parser, environ):
        pass

    @classmethod
    def run(cls, **kwargs):
        cls.captured = kwargs


class DummyBackendWithTasks(BaseBackend):
    def get_table_definition(self):
        raise NotImplementedError()

    @classmethod
    def admin_tasks(cls):
        return {"fake-task": CaptureTask}


def _register_fake_backend_alias(mocker, backend_class):
    """Patch BACKEND_ALIASES so the `fake` alias resolves to `backend_class`."""
    mocker.patch.dict(
        "ehrql.__main__.BACKEND_ALIASES",
        {"fake": f"{backend_class.__module__}.{backend_class.__name__}"},
    )


def test_backend_admin_help_lists_backends(capsys):
    with pytest.raises(SystemExit):
        main(["backend-admin", "--help"])
    captured = capsys.readouterr()
    for alias in BACKEND_ALIASES:
        assert alias in captured.out


def test_backend_admin_backend_with_no_tasks_prints_message(mocker, capsys):
    _register_fake_backend_alias(mocker, DummyBackend)

    main(["backend-admin", "fake"])
    captured = capsys.readouterr()

    assert "No backend-admin tasks are currently defined" in captured.err


def test_backend_admin_invalid_backend(capsys):
    with pytest.raises(SystemExit):
        main(["backend-admin", "nope"])
    captured = capsys.readouterr()
    assert "nope" in captured.err


def test_backend_admin_backend_help_lists_tasks_when_present(capsys, mocker):
    _register_fake_backend_alias(mocker, DummyBackendWithTasks)
    with pytest.raises(SystemExit):
        main(["backend-admin", "fake", "--help"])
    captured = capsys.readouterr()
    assert "fake-task" in captured.out


def test_backend_admin_passes_backend_class_to_task(mocker):
    _register_fake_backend_alias(mocker, DummyBackendWithTasks)
    main(["backend-admin", "fake", "fake-task"])
    assert CaptureTask.captured["backend_class"] is DummyBackendWithTasks


def test_backend_admin_emisv2_tasks_listed_in_help(capsys):
    # Exercise the entrypoint for emisv2 tasks
    with pytest.raises(SystemExit):
        main(["backend-admin", "emisv2", "--help"])
    captured = capsys.readouterr()
    assert "cleanup-temp-tables" in captured.out


def test_backend_admin_resolves_backend_from_dotted_path():
    # Confirm that we can get the backend by dotted import path
    dotted_path = f"{DummyBackendWithTasks.__module__}.{DummyBackendWithTasks.__name__}"
    main(["backend-admin", dotted_path, "fake-task"])
    assert CaptureTask.captured["backend_class"] is DummyBackendWithTasks


def test_backend_admin_treats_expectations_backend_as_no_backend(capsys):
    # `backend_from_id` returns None for the legacy "expectations" and "test"
    # backend names; dispatch should fall back to printing help.
    with pytest.raises(SystemExit):
        main(["backend-admin", "expectations"])
    captured = capsys.readouterr()
    assert "usage: ehrql backend-admin" in captured.out


def test_backend_admin_resolves_backend_from_env_var(mocker, capsys):
    # backend selection via env var should reach the backend's own
    # dispatch the same way an explicit positional does.
    _register_fake_backend_alias(mocker, DummyBackend)
    main(["backend-admin"], environ={"OPENSAFELY_BACKEND": "fake"})
    captured = capsys.readouterr()
    assert "No backend-admin tasks are currently defined" in captured.err


class BadBackend:
    # This backend has a `get_table_definition` so `backend_from_id` accepts it, but
    # doesn't extend BaseBackend, so lacks `run_admin_command` which is required for
    # backend-admin tasks
    def get_table_definition(self):
        raise NotImplementedError()


def test_backend_admin_backend_without_run_admin_command(capsys):
    dotted_path = f"{BadBackend.__module__}.{BadBackend.__name__}"
    with pytest.raises(SystemExit) as exc:
        main(["backend-admin", dotted_path])
    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert "does not support backend-admin tasks" in captured.err


def test_backend_admin_backend_with_tasks_no_task_prints_help(mocker, capsys):
    # Invoking `backend-admin <backend>` with no task hits the default
    # `show_help` function on the backend's task parser.
    _register_fake_backend_alias(mocker, DummyBackendWithTasks)
    with pytest.raises(SystemExit):
        main(["backend-admin", "fake"])
    captured = capsys.readouterr()
    assert "fake-task" in captured.out
