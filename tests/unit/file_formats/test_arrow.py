import pytest

from databuilder.column_specs import ColumnSpec
from databuilder.file_formats.arrow import batch_and_transpose, schema_from_column_specs
from databuilder.sqlalchemy_types import TYPE_MAP


# Check we can convert every type in TYPE_MAP to a pyarrow type
@pytest.mark.parametrize("type_", list(TYPE_MAP.keys()))
def test_schema_from_column_specs(type_):
    columns_specs = {"some_col": ColumnSpec(type_)}
    schema = schema_from_column_specs(columns_specs)
    assert schema.names == ["some_col"]


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
