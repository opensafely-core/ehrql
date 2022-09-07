import datetime
import gzip
from pathlib import Path

import pytest

from databuilder.column_specs import ColumnSpec
from databuilder.query_language import Dataset, PatientFrame, Series, table
from databuilder.validate_dummy_data import (
    ValidationError,
    validate_csv_against_spec,
    validate_dummy_data_file,
    validate_file_types_match,
    validate_headers,
    validate_str_against_spec,
)


@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)


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
        with pytest.raises(ValidationError):
            validate_file_types_match(path_a, path_b)


@pytest.mark.parametrize("value,is_valid", [("1999", True), ("not_an_int", False)])
@pytest.mark.parametrize("gzipped,extension", [(False, "csv"), (True, "csv.gz")])
def test_validate_dummy_data_file_csv(tmp_path, value, is_valid, gzipped, extension):
    dataset = Dataset()
    dataset.set_population(patients.exists_for_patient())
    dataset.year = patients.date_of_birth.year

    dummy_data = f"patient_id,year\n123,1980\n456,{value}"

    dummy_data_path = tmp_path / f"dummy.{extension}"
    if gzipped:
        dummy_data_path.write_bytes(gzip.compress(dummy_data.encode()))
    else:
        dummy_data_path.write_text(dummy_data)

    if is_valid:
        validate_dummy_data_file(dataset, dummy_data_path)
    else:
        with pytest.raises(ValidationError, match="row 2, column 'year': Invalid int"):
            validate_dummy_data_file(dataset, dummy_data_path)


def test_validate_dummy_data_file_unsupported_file_type():
    with pytest.raises(ValidationError, match="Unsupported file type: .foo"):
        validate_dummy_data_file(Dataset(), Path("bad_extension.foo"))


@pytest.mark.parametrize(
    "csv,error",
    [
        # Happy path (with allowed null)
        ("patient_id,age\n1,65\n2,", None),
        # Null in non-nullable colum
        ("patient_id,age\n1,65\n,25", "NULL value not allowed here"),
        # Wrong headers
        ("patient_id,oldness_score\n1,65", "Missing columns"),
        # Invalid type
        ("patient_id,age\n1,sixty", "Invalid int"),
        # Too many columns
        ("patient_id,age\n1,65,0", "Too many columns on row 1"),
        # Too few columns
        ("patient_id,age\n1", "Too few columns on row 1"),
        # Nullable colum with no non-null values
        ("patient_id,age\n1,\n2,", "Columns are empty: age"),
    ],
)
def test_validate_csv_against_spec(csv, error):
    specs = {
        "patient_id": ColumnSpec(int, nullable=False),
        "age": ColumnSpec(int, nullable=True),
    }
    csv_file = iter(csv.splitlines(keepends=True))

    if error is None:
        validate_csv_against_spec(csv_file, specs)
    else:
        with pytest.raises(ValidationError, match=error):
            validate_csv_against_spec(csv_file, specs)


@pytest.mark.parametrize(
    "headers,error",
    [
        (["foo", "bar", "baz"], None),
        (["foo", "baz"], r"Missing columns"),
        (["foo", "bar", "baz", "boo"], r"Unexpected columns"),
        (["bar", "baz", "boo"], r"Missing columns[\s\S]*Unexpected columns"),
        (["foo", "baz", "bar"], r"Headers not in expected order"),
    ],
)
def test_validate_headers(headers, error):
    expected = ["foo", "bar", "baz"]
    if error is None:
        validate_headers(headers, expected)
    else:
        with pytest.raises(ValidationError, match=error):
            validate_headers(headers, expected)


@pytest.mark.parametrize(
    "value,spec,error",
    [
        # Null handling
        ("foo", ColumnSpec(str), None),
        ("", ColumnSpec(str, nullable=True), None),
        ("", ColumnSpec(str, nullable=False), "NULL value not allowed here"),
        # Bool
        ("0", ColumnSpec(bool), None),
        ("1", ColumnSpec(bool), None),
        ("3", ColumnSpec(bool), "Invalid bool, must be '0' or '1'"),
        # Int
        ("123", ColumnSpec(int), None),
        ("-123", ColumnSpec(int), None),
        ("0.5", ColumnSpec(int), "Invalid int"),
        # Float
        ("123", ColumnSpec(float), None),
        ("123.456", ColumnSpec(float), None),
        ("-123.456", ColumnSpec(float), None),
        ("1/2", ColumnSpec(float), "Invalid float"),
        # Date
        ("2020-02-29", ColumnSpec(datetime.date), None),
        ("2021-02-29", ColumnSpec(datetime.date), "Invalid date"),
        ("2021-2-2", ColumnSpec(datetime.date), "Invalid date"),
    ],
)
def test_validate_str_against_spec(value, spec, error):
    if error is None:
        validate_str_against_spec(value, spec)
    else:
        with pytest.raises(ValidationError, match=error):
            validate_str_against_spec(value, spec)
