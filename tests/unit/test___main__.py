import pytest

from databuilder.__main__ import (
    ArgumentTypeError,
    backend_from_id,
    import_string,
    main,
    query_engine_from_id,
)


def test_no_args(capsys):
    # Verify that when databuilder is called without arguments, help text is shown.
    main([])
    captured = capsys.readouterr()
    assert "usage: databuilder" in captured.out


def test_generate_dataset(mocker, tmp_path):
    # Verify that the generate_dataset subcommand can be invoked when
    # DATABASE_URL is set.
    patched = mocker.patch("databuilder.__main__.generate_dataset")
    env = {"DATABASE_URL": "scheme:path"}
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
    ]
    main(argv, env)
    patched.assert_called_once()


def test_pass_dummy_data(mocker, tmp_path):
    # Verify that the pass_dummy_data subcommand can be invoked when
    # --dummy-data-file is provided.
    patched = mocker.patch("databuilder.__main__.pass_dummy_data")
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
        "--dummy-data-file",
        str(tmp_path / "dummy-data.csv"),
        "--backend",
        "expectations",
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_dataset_if_both_dsn_and_dummy_data_are_provided(mocker, tmp_path):
    # This happens when studies with dummy data are run in the backend.
    patched = mocker.patch("databuilder.__main__.generate_dataset")
    env = {"DATABASE_URL": "scheme:path"}
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
        "--dummy-data-file",
        str(tmp_path / "dummy-data.csv"),
    ]
    main(argv, env)
    patched.assert_called_once()


def test_generate_dataset_without_dsn_or_dummy_data(capsys, tmp_path):
    # Verify that a helpful message is shown when the generate_dataset
    # subcommand is invoked but DATABASE_URL is not set and --dummy-data-file
    # is not provided.
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        str(dataset_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert (
        "one of --dummy-data-file, --dsn or DATABASE_URL environment variable is required"
        in captured.err
    )


def test_generate_dataset_rejects_unknown_extension(capsys):
    argv = [
        "generate-dataset",
        # We just need any old Python file to supply as the dataset
        __file__,
        "--output",
        "out_file.badformat",
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert ".badformat' is not a supported format" in captured.err


def test_dump_dataset_sql(mocker, tmp_path):
    # Verify that the dump dataset sql subcommand can be invoked.
    patched = mocker.patch("databuilder.__main__.dump_dataset_sql")
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "dump-dataset-sql",
        "--backend",
        "databuilder.backends.tpp.TPPBackend",
        str(dataset_definition_path),
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_measures(mocker, tmp_path):
    # Verify that the generate_measures subcommand can be invoked.
    patched = mocker.patch("databuilder.__main__.generate_measures")
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-measures",
        str(dataset_definition_path),
    ]
    main(argv)
    patched.assert_called_once()


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


def test_import_string():
    assert import_string("databuilder.__main__.main") is main


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
    def get_results(self):
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


class DummyBackend:
    def get_table_expression(self):
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
