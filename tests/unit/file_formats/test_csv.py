import datetime
from io import StringIO

import pytest

from databuilder.column_specs import ColumnSpec
from databuilder.file_formats.csv import write_dataset_csv_lines
from databuilder.sqlalchemy_types import TYPE_MAP


@pytest.mark.parametrize(
    "type_,value,expected",
    [
        (bool, None, ""),
        (bool, True, "1"),
        (bool, False, "0"),
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
def test_write_dataset_csv_lines(type_, value, expected):
    column_specs = {
        "patient_id": ColumnSpec(int),
        "value": ColumnSpec(type_),
    }
    results = [(123, value)]
    output = StringIO()
    write_dataset_csv_lines(output, results, column_specs)
    assert output.getvalue() == f"patient_id,value\r\n123,{expected}\r\n"


def test_write_dataset_csv_lines_params_are_exhaustive():
    # This is dirty but useful, I think. It checks that the parameters to the test
    # include at least one of every type in `sqlalchemy_types`.
    params = test_write_dataset_csv_lines.pytestmark[0].args[1]
    types = [arg[0] for arg in params]
    assert set(types) == set(TYPE_MAP)
