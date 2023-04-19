import pyarrow
import pytest

from databuilder.file_formats.arrow import (
    ArrowDatasetReader,
    batch_and_transpose,
    get_schema_and_convertor,
    smallest_int_type_for_range,
)
from databuilder.query_model.column_specs import ColumnSpec
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


def test_batch_and_transpose():
    row_wise = [
        (1, "a"),
        (2, "b"),
        (3, "c"),
        (4, "d"),
        (5, "e"),
        (6, "f"),
        (7, "g"),
        (8, "h"),
    ]
    batched_column_wise = batch_and_transpose(row_wise, 3)
    assert list(batched_column_wise) == [
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


def test_smallest_int_type_for_range_default():
    assert smallest_int_type_for_range(None, 0) == pyarrow.int64()
    assert smallest_int_type_for_range(0, None) == pyarrow.int64()


def test_read_dataset_arrow(tmp_path):
    # test that arrow file successfully round-trips
    file_data = [
        (1, 100),
        (3, 300),
    ]
    path = tmp_path / "input.arrow"

    columns = ["patient_id", "n"]
    input_table = pyarrow.Table.from_pylist([dict(zip(columns, f)) for f in file_data])
    pyarrow.feather.write_feather(input_table, str(path), compression="zstd")

    column_specs = {"patient_id": ColumnSpec(int), "n": ColumnSpec(int)}
    with ArrowDatasetReader(path, column_specs) as reader:
        lines = list(reader)

    assert lines == file_data
