import datetime
from io import StringIO
from pathlib import Path

import pytest

from ehrql.file_formats.csv import (
    BaseCSVRowsReader,
    FileValidationError,
    create_column_parser,
    write_rows_csv_lines,
)
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.sqlalchemy_types import TYPE_MAP


@pytest.mark.parametrize(
    "type_,value,expected",
    [
        (bool, None, ""),
        (bool, True, "T"),
        (bool, False, "F"),
        (int, None, ""),
        (int, 123, "123"),
        (float, None, ""),
        (float, 0.5, "0.5"),
        (str, None, ""),
        (str, "foo", "foo"),
        (datetime.date, None, ""),
        (datetime.date, datetime.date(2020, 10, 20), "2020-10-20"),
    ],
)
def test_write_rows_csv_lines(type_, value, expected):
    column_specs = {
        "patient_id": ColumnSpec(int),
        "value": ColumnSpec(type_),
    }
    results = [(123, value)]
    output = StringIO()
    write_rows_csv_lines(output, results, column_specs)
    assert output.getvalue() == f"patient_id,value\r\n123,{expected}\r\n"


def test_write_rows_csv_lines_params_are_exhaustive():
    # This is dirty but useful, I think. It checks that the parameters to the test
    # include at least one of every type in `sqlalchemy_types`.
    params = test_write_rows_csv_lines.pytestmark[0].args[1]
    types = [arg[0] for arg in params]
    assert set(types) == set(TYPE_MAP)


# Allow testing CSV reader without needing a file on disk
class StringIOCSVRowsReader(BaseCSVRowsReader):
    def __init__(self, csv_data, column_specs):
        self.csv_data = csv_data
        super().__init__(Path("/dev/null"), column_specs)

    def _open(self):
        self._fileobj = StringIO(self.csv_data)


@pytest.mark.parametrize(
    "csv,error",
    [
        # Happy path (with allowed null)
        (
            "patient_id,age\n1,65\n2,",
            None,
        ),
        # Null in non-nullable colum
        (
            "patient_id,age\n1,65\n,25",
            "row 2: NULL value in non-nullable column 'patient_id'",
        ),
        # Wrong headers
        (
            "patient_id,oldness_score\n1,65",
            "Missing columns",
        ),
        # Invalid type
        (
            "patient_id,age\n1,sixty",
            "row 1: column 'age': invalid literal for int",
        ),
        # Too many columns
        (
            "patient_id,age\n1,65,0",
            "row 1: expected 2 columns but got 3",
        ),
        # Too few columns
        (
            "patient_id,age\n1",
            "row 1: expected 2 columns but got 1",
        ),
    ],
)
def test_read_rows_csv_lines(csv, error):
    specs = {
        "patient_id": ColumnSpec(int, nullable=False),
        "age": ColumnSpec(int, nullable=True),
    }

    if error is None:
        StringIOCSVRowsReader(csv, specs).close()
    else:
        with pytest.raises(FileValidationError, match=error):
            StringIOCSVRowsReader(csv, specs)


@pytest.mark.parametrize(
    "value,spec,expected,error",
    [
        # Null handling
        ("", ColumnSpec(str, nullable=True), None, None),
        (
            "",
            ColumnSpec(str, nullable=False),
            None,
            "NULL value in non-nullable column",
        ),
        # Str
        ("foo", ColumnSpec(str), "foo", None),
        # Bool
        ("F", ColumnSpec(bool), False, None),
        ("T", ColumnSpec(bool), True, None),
        ("t", ColumnSpec(bool), None, "invalid boolean, must be 'T' or 'F'"),
        ("3", ColumnSpec(bool), None, "invalid boolean, must be 'T' or 'F'"),
        # Int
        ("123", ColumnSpec(int), 123, None),
        ("-123", ColumnSpec(int), -123, None),
        ("0.5", ColumnSpec(int), None, "invalid literal for int"),
        # Float
        ("123", ColumnSpec(float), 123.0, None),
        ("123.456", ColumnSpec(float), 123.456, None),
        ("-123.456", ColumnSpec(float), -123.456, None),
        ("1/2", ColumnSpec(float), None, "could not convert string to float"),
        # Date
        ("2020-02-29", ColumnSpec(datetime.date), datetime.date(2020, 2, 29), None),
        (
            "2021-02-29",
            ColumnSpec(datetime.date),
            None,
            "day is out of range for month",
        ),
        ("2021-2-2", ColumnSpec(datetime.date), None, "Invalid isoformat string"),
        # Categoricals
        (
            "foo",
            ColumnSpec(str, categories=("foo", "bar")),
            "foo",
            None,
        ),
        (
            "baz",
            ColumnSpec(str, categories=("foo", "bar")),
            None,
            "'baz' not in valid categories",
        ),
    ],
)
def test_create_column_parser(value, spec, expected, error):
    headers = ["value"]
    row = [value]

    parser = create_column_parser(headers, "value", spec)
    if error is None:
        assert parser(row) == expected
    else:
        with pytest.raises(ValueError, match=error):
            parser(row)


def test_create_column_parser_params_are_exhaustive():
    # This is dirty but useful, I think. It checks that the parameters to the test
    # include at least one of every type in `sqlalchemy_types`.
    params = test_create_column_parser.pytestmark[0].args[1]
    types = [arg[1].type for arg in params]
    assert set(types) == set(TYPE_MAP)
