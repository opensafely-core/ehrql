import pytest

from databuilder.__main__ import main


def test_no_args(capsys):
    # Verify that when databuilder is called without arguments, help text is shown.
    main([])
    captured = capsys.readouterr()
    assert "usage: databuilder" in captured.out


def test_generate_dataset(mocker, monkeypatch, tmp_path):
    # Verify that the generate_dataset subcommand can be invoked when
    # DATABASE_URL is set.
    patched = mocker.patch("databuilder.__main__.generate_dataset")
    monkeypatch.setenv("DATABASE_URL", "scheme:path")
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        "--dataset-definition",
        str(dataset_definition_path),
    ]
    main(argv)
    patched.assert_called_once()


def test_pass_dummy_data(mocker, tmp_path):
    # Verify that the pass_dummy_data subcommand can be invoked when
    # --dummy-data-file is provided.
    patched = mocker.patch("databuilder.__main__.pass_dummy_data")
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        "--dataset-definition",
        str(dataset_definition_path),
        "--dummy-data-file",
        str(tmp_path / "dummy-data.csv"),
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_dataset_if_both_db_url_and_dummy_data_are_provided(
    mocker, monkeypatch, tmp_path
):
    # This happens when studies with dummy data are run in the backend.
    patched = mocker.patch("databuilder.__main__.generate_dataset")
    monkeypatch.setenv("DATABASE_URL", "scheme:path")
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        "--dataset-definition",
        str(dataset_definition_path),
        "--dummy-data-file",
        str(tmp_path / "dummy-data.csv"),
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_dataset_without_database_url_or_dummy_data(capsys, tmp_path):
    # Verify that a helpful message is shown when the generate_dataset
    # subcommand is invoked but DATABASE_URL is not set and --dummy-data-file
    # is not provided.
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "generate-dataset",
        "--dataset-definition",
        str(dataset_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert (
        "either --dummy-data-file or DATABASE_URL environment variable is required"
        in captured.err
    )


def test_dump_dataset_sql(mocker, tmp_path):
    # Verify that the dump dataset sql subcommand can be invoked.
    patched = mocker.patch("databuilder.__main__.validate_dataset")
    dataset_definition_path = tmp_path / "dataset.py"
    dataset_definition_path.touch()
    argv = [
        "dump-dataset-sql",
        "--dataset-definition",
        str(dataset_definition_path),
        "databuilder.backends.tpp.TPPBackend",
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
        "--dataset-definition",
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
        "--dataset-definition",
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
        "--dataset-definition",
        str(dataset_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "dataset.cpp is not a Python file" in captured.err
