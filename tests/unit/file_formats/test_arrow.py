import pytest

from databuilder.column_specs import ColumnSpec
from databuilder.file_formats.arrow import batch_and_transpose, get_schema_and_convertor
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
