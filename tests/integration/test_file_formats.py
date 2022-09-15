import gzip

import pyarrow.feather
import pytest

from databuilder.column_specs import ColumnSpec
from databuilder.file_formats import (
    FILE_FORMATS,
    ValidationError,
    validate_dataset,
    write_dataset,
)


@pytest.mark.parametrize("basename", [None, "file.csv", "file.csv.gz"])
def test_write_dataset_csv(tmp_path, capsys, basename):
    if basename is None:
        filename = None
    else:
        filename = tmp_path / "somedir" / basename

    column_specs = {
        "patient_id": ColumnSpec(int),
        "year_of_birth": ColumnSpec(int),
        "sex": ColumnSpec(str),
    }
    results = [
        (123, 1980, "F"),
        (456, None, None),
        (789, 1999, "M"),
    ]

    write_dataset(filename, results, column_specs)

    if basename is None:
        output = capsys.readouterr().out
    elif basename.endswith(".csv.gz"):
        with gzip.open(filename, "rt") as f:
            output = f.read()
    elif basename.endswith(".csv"):
        output = filename.read_text()
    else:
        assert False

    assert output.splitlines() == [
        "patient_id,year_of_birth,sex",
        "123,1980,F",
        "456,,",
        "789,1999,M",
    ]


def test_write_dataset_arrow(tmp_path):
    filename = tmp_path / "somedir" / "file.arrow"
    column_specs = {
        "patient_id": ColumnSpec(int),
        "year_of_birth": ColumnSpec(int),
        "sex": ColumnSpec(str),
    }
    results = [
        (123, 1980, "F"),
        (456, None, None),
        (789, 1999, "M"),
    ]
    write_dataset(filename, results, column_specs)

    table = pyarrow.feather.read_table(filename)
    output_columns = table.column_names
    output_rows = [tuple(d.values()) for d in table.to_pylist()]

    assert output_columns == list(column_specs.keys())
    assert output_rows == results


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_validate_dataset_happy_path(tmp_path, extension):
    filename = tmp_path / f"dataset{extension}"
    column_specs = {
        "patient_id": ColumnSpec(int),
        "year_of_birth": ColumnSpec(int),
    }
    results = [
        (123, 1980),
        (456, 1999),
    ]
    write_dataset(filename, results, column_specs)

    validate_dataset(filename, column_specs)


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_validate_dataset_type_mismatch(tmp_path, extension):
    filename = tmp_path / f"dataset{extension}"
    column_specs_1 = {
        "patient_id": ColumnSpec(int),
        "sex": ColumnSpec(str),
    }
    results = [
        (123, "F"),
        (456, "M"),
    ]
    write_dataset(filename, results, column_specs_1)

    # Create another set of columns with the same names but different types, and check
    # that the file *doesn't* validate against this
    column_specs_2 = {
        "patient_id": ColumnSpec(int),
        "sex": ColumnSpec(int),
    }

    errors = {
        ".arrow": "File does not have expected schema",
        ".csv": "invalid literal for int",
        ".csv.gz": "invalid literal for int",
    }

    with pytest.raises(ValidationError, match=errors[extension]):
        validate_dataset(filename, column_specs_2)
