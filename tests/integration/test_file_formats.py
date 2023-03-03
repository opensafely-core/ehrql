import pytest

from databuilder.file_formats import (
    FILE_FORMATS,
    ValidationError,
    validate_dataset,
    write_dataset,
)
from databuilder.query_model.column_specs import ColumnSpec


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_write_and_validate_dataset_happy_path(tmp_path, extension):
    filename = tmp_path / f"dataset{extension}"
    column_specs = {
        "patient_id": ColumnSpec(int),
        "year_of_birth": ColumnSpec(int),
        "category": ColumnSpec(str, categories=("a", "b")),
    }
    results = [
        (123, 1980, "a"),
        (456, 1999, "b"),
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


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_validate_dataset_category_mismatch(tmp_path, extension):
    filename = tmp_path / f"dataset{extension}"
    column_specs_1 = {
        "patient_id": ColumnSpec(int),
        "category": ColumnSpec(str, categories=("a", "b")),
    }
    results = [
        (123, "a"),
        (456, "b"),
    ]
    write_dataset(filename, results, column_specs_1)

    column_specs_2 = {
        "patient_id": ColumnSpec(int),
        "category": ColumnSpec(str, categories=("x", "y")),
    }

    errors = {
        ".arrow": "Unexpected categories in column 'category'",
        ".csv": "'a' not in valid categories: 'x', 'y'",
        ".csv.gz": "'a' not in valid categories: 'x', 'y'",
    }

    with pytest.raises(ValidationError, match=errors[extension]):
        validate_dataset(filename, column_specs_2)


@pytest.mark.parametrize("extension", list(FILE_FORMATS.keys()))
def test_write_dataset_rejects_unexpected_category(tmp_path, extension):
    filename = tmp_path / f"dataset{extension}"
    column_specs_1 = {
        "patient_id": ColumnSpec(int),
        "category": ColumnSpec(str, categories=("a", "b")),
    }
    results = [
        (123, "a"),
        (456, "bad_category"),
    ]

    # Different file formats may raise different exception classes here, but the
    # important thing is that they raise some kind of error and don't just write out
    # invalid data
    with pytest.raises(Exception, match="bad_category"):
        write_dataset(filename, results, column_specs_1)
