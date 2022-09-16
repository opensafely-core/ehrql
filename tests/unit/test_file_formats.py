from pathlib import Path

import pytest

from databuilder.file_formats import (
    ValidationError,
    get_file_extension,
    validate_file_types_match,
)


@pytest.mark.parametrize(
    "a,b,matches",
    [
        ("testfile.feather", "other.feather", True),
        ("testfile.csv.gz", "other.csv.gz", True),
        ("testfile.dta", "testfile.dta.gz", False),
        ("testfile.csv", "testfile.tsv", False),
    ],
)
def test_validate_file_types_match(a, b, matches):
    path_a = Path(a)
    path_b = Path(b)
    if matches:
        validate_file_types_match(path_a, path_b)
    else:
        with pytest.raises(
            ValidationError,
            match="Dummy data file does not have the same file extension",
        ):
            validate_file_types_match(path_a, path_b)


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
