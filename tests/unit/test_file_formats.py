from pathlib import Path

import pytest

from databuilder.file_formats import get_file_extension


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
