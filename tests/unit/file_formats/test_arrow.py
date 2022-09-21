import pyarrow
import pytest

from databuilder.column_specs import ColumnSpec
from databuilder.file_formats.arrow import (
    batch_and_transpose,
    get_schema_and_convertor,
    smallest_int_type_for_range,
)
from databuilder.sqlalchemy_types import TYPE_MAP


# Check we can convert every type in TYPE_MAP to a pyarrow type
@pytest.mark.parametrize("type_", list(TYPE_MAP.keys()))
def test_get_schema_and_convertor(type_):
    columns_specs = {"some_col": ColumnSpec(type_)}
    schema, batch_to_pyarrow = get_schema_and_convertor(columns_specs)
    assert schema.names == ["some_col"]

    batch = [[None]]
    pyarrow_batch = batch_to_pyarrow(batch)
    assert pyarrow_batch[0].type == schema.field(0).type


def test_batch_and_transponse():
    results = [
        (1, "a"),
        (2, "b"),
        (3, "c"),
        (4, "d"),
        (5, "e"),
        (6, "f"),
        (7, "g"),
        (8, "h"),
    ]
    batched = batch_and_transpose(results, 3)
    assert list(batched) == [
        [(1, 2, 3), ("a", "b", "c")],
        [(4, 5, 6), ("d", "e", "f")],
        [(7, 8), ("g", "h")],
    ]


@pytest.mark.parametrize(
    "min_value,max_value,expected_width",
    [
        (1, 2**8 - 1, 8),
        (1, 2**16 - 1, 16),
        (1, 2**24 - 1, 32),
        (1, 2**32 - 1, 32),
        (1, 2**40 - 1, 64),
        (1, 2**64 - 1, 64),
        (-1, 2**7 - 1, 8),
        (-1, 2**15 - 1, 16),
        (-1, 2**24 - 1, 32),
        (-1, 2**31 - 1, 32),
        (-1, 2**40 - 1, 64),
        (-1, 2**63 - 1, 64),
    ],
)
def test_smallest_int_type_for_range(min_value, max_value, expected_width):
    type_ = smallest_int_type_for_range(min_value, max_value)
    roundtripped = pyarrow.array([min_value, max_value], type=type_).to_pylist()

    assert [min_value, max_value] == roundtripped
    assert type_.bit_width == expected_width
