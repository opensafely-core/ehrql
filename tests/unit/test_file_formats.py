from pathlib import Path

import pytest

from databuilder.file_formats import ValidationError, get_file_extension, read_dataset


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


def test_read_dataset_rejects_unsupported_file_types():
    with pytest.raises(ValidationError, match="Unsupported file type: .xyz"):
        read_dataset(Path("some_file.xyz"), {})


def test_read_dataset_raises_error_for_missing_files():
    missing_file = Path(__file__).parent / "no_such_file.csv"
    with pytest.raises(ValidationError, match=f"Missing file: {missing_file}"):
        read_dataset(missing_file, {})
