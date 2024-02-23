from pathlib import Path

import pytest

from ehrql.file_formats import (
    ValidationError,
    get_extension_from_directory,
    get_file_extension,
    get_table_filename,
    read_rows,
    split_directory_and_extension,
)
from ehrql.file_formats.arrow import ArrowRowsReader
from ehrql.file_formats.csv import CSVGZRowsReader, CSVRowsReader


@pytest.mark.parametrize(
    "filename,extension",
    [
        (None, ".csv"),
        (Path("a/b.c/file.txt"), ".txt"),
        (Path("a/b.c/file.txt.foo"), ".foo"),
        (Path("a/b.c/file.txt.gz"), ".txt.gz"),
        (Path("a/b.c/file"), ""),
    ],
)
def test_get_file_extension(filename, extension):
    assert get_file_extension(filename) == extension


def test_read_rows_rejects_unsupported_file_types():
    with pytest.raises(ValidationError, match="Unsupported file type: .xyz"):
        read_rows(Path("some_file.xyz"), {})


def test_read_rows_raises_error_for_missing_files():
    missing_file = Path(__file__).parent / "no_such_file.csv"
    with pytest.raises(ValidationError, match=f"Missing file: {missing_file}"):
        read_rows(missing_file, {})


@pytest.mark.parametrize(
    "reader_class",
    [
        CSVRowsReader,
        CSVGZRowsReader,
        ArrowRowsReader,
    ],
)
def test_rows_reader_constructor_rejects_non_path(reader_class):
    with pytest.raises(ValidationError, match="must be a pathlib.Path instance"):
        reader_class("some/string/path", {})


def test_get_extension_from_directory(tmp_path):
    directory = tmp_path / "some_dir"
    directory.mkdir()
    (directory / "file_a.csv.gz").touch()
    (directory / "file_b.csv.gz").touch()
    (directory / "README.txt").touch()
    assert get_extension_from_directory(directory) == ".csv.gz"


def test_get_extension_from_directory_missing(tmp_path):
    with pytest.raises(ValidationError, match="Missing directory"):
        get_extension_from_directory(tmp_path / "no_such_dir")


def test_get_extension_from_directory_with_wrong_type(tmp_path):
    directory = tmp_path / "not_a_dir"
    directory.touch()
    with pytest.raises(ValidationError, match="Not a directory"):
        get_extension_from_directory(directory)


def test_get_extension_from_directory_without_supported_extensions(tmp_path):
    directory = tmp_path / "some_dir"
    directory.mkdir()
    (directory / "file_a.jpg").touch()
    (directory / "file_b.docx").touch()
    with pytest.raises(ValidationError, match="No supported file formats found"):
        get_extension_from_directory(directory)


def test_get_extension_from_directory_with_ambiguous_extensions(tmp_path):
    directory = tmp_path / "some_dir"
    directory.mkdir()
    (directory / "file_a.csv").touch()
    (directory / "file_b.arrow").touch()
    with pytest.raises(
        ValidationError,
        match=r"Found multiple file formats \(\.arrow, \.csv\)",
    ):
        get_extension_from_directory(directory)


def test_get_table_filename_escapes_problematic_characters():
    filename = get_table_filename(
        Path("parent"),
        "bad/ table /name/",
        ".csv",
    )
    assert filename == Path("parent/bad%2F%20table%20%2Fname%2F.csv")


@pytest.mark.parametrize(
    "filename,expected_dir,expected_ext",
    [
        ("some/dir:csv", "some/dir", ".csv"),
        ("some/dir", "some/dir", ""),
        ("some/dir/:csv", "some/dir", ".csv"),
    ],
)
def test_split_directory_and_extension(filename, expected_dir, expected_ext):
    directory, extension = split_directory_and_extension(Path(filename))
    assert directory == Path(expected_dir)
    assert extension == expected_ext
