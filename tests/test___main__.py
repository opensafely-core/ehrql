import pytest

from databuilder.__main__ import main


def test_no_args(capsys):
    # Verify that when databuilder is called without arguments, help text is shown.
    main([])
    captured = capsys.readouterr()
    assert "usage: databuilder" in captured.out


def test_generate_dataset_with_database_url(mocker, monkeypatch, tmp_path):
    # Verify that the generate_dataset subcommand can be invoked when
    # DATABASE_URL is set.
    patched = mocker.patch("databuilder.__main__.run_cohort_action")
    monkeypatch.setenv("DATABASE_URL", "scheme:path")
    cohort_definition_path = tmp_path / "cohort.py"
    cohort_definition_path.touch()
    argv = [
        "generate_dataset",
        "--cohort-definition",
        str(cohort_definition_path),
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_dataset_with_dummy_data(mocker, tmp_path):
    # Verify that the generate_dataset subcommand can be invoked when
    # --dummy-data-file is provided.
    patched = mocker.patch("databuilder.__main__.run_cohort_action")
    cohort_definition_path = tmp_path / "cohort.py"
    cohort_definition_path.touch()
    dummy_data_path = tmp_path / "dummy-data.csv"
    dummy_data_path.touch()
    argv = [
        "generate_dataset",
        "--cohort-definition",
        str(cohort_definition_path),
        "--dummy-data-file",
        str(dummy_data_path),
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_dataset_without_database_url_or_dummy_data(capsys, tmp_path):
    # Verify that a helpful message is shown when the generate_dataset
    # subcommand is invoked but DATABASE_URL is not set and --dummy-data-file
    # is not provided.
    cohort_definition_path = tmp_path / "cohort.py"
    cohort_definition_path.touch()
    argv = [
        "generate_dataset",
        "--cohort-definition",
        str(cohort_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert (
        "either --dummy-data-file or DATABASE_URL environment variable is required"
        in captured.err
    )


def test_generate_docs(mocker):
    patched = mocker.patch("databuilder.__main__.generate_docs")

    argv = [
        "generate_docs",
    ]
    main(argv)

    patched.assert_called_once()


def test_validate_cohort(mocker, tmp_path):
    # Verify that the validate_cohort subcommand can be invoked.
    patched = mocker.patch("databuilder.__main__.run_cohort_action")
    cohort_definition_path = tmp_path / "cohort.py"
    cohort_definition_path.touch()
    argv = [
        "validate_cohort",
        "--cohort-definition",
        str(cohort_definition_path),
        "tpp",
    ]
    main(argv)
    patched.assert_called_once()


def test_generate_measures(mocker, tmp_path):
    # Verify that the generate_measures subcommand can be invoked.
    patched = mocker.patch("databuilder.__main__.generate_measures")
    cohort_definition_path = tmp_path / "cohort.py"
    cohort_definition_path.touch()
    argv = [
        "generate_measures",
        "--cohort-definition",
        str(cohort_definition_path),
    ]
    main(argv)
    patched.assert_called_once()


def test_existing_python_file_missing_file(capsys, tmp_path):
    # Verify that a helpful message is shown when a command is invoked with a path to a
    # file that should exist but doesn't.
    cohort_definition_path = tmp_path / "cohort.py"
    argv = [
        "generate_dataset",
        "--cohort-definition",
        str(cohort_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "cohort.py does not exist" in captured.err


def test_existing_python_file_unpythonic_file(capsys, tmp_path):
    # Verify that a helpful message is shown when a command is invoked with a path to a
    # file that should be a Python file but isn't.
    cohort_definition_path = tmp_path / "cohort.cpp"
    cohort_definition_path.touch()
    argv = [
        "generate_dataset",
        "--cohort-definition",
        str(cohort_definition_path),
    ]
    with pytest.raises(SystemExit):
        main(argv)
    captured = capsys.readouterr()
    assert "cohort.cpp is not a Python file" in captured.err


def test_test_connection(monkeypatch, database, capsys):
    monkeypatch.setenv("BACKEND", "tpp")
    monkeypatch.setenv("DATABASE_URL", database.host_url())
    argv = ["test_connection"]
    main(argv)
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out
