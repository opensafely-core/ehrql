import pyarrow.feather

from ehrql.file_formats import write_dataset
from ehrql.query_model.column_specs import ColumnSpec


def test_write_dataset_arrow(tmp_path):
    filename = tmp_path / "somedir" / "file.arrow"
    column_specs = {
        "patient_id": ColumnSpec(int),
        "year_of_birth": ColumnSpec(int, min_value=1900, max_value=2100),
        "sex": ColumnSpec(str, categories=("M", "F", "I")),
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
    categories = table.column("sex").chunk(0).dictionary.to_pylist()
    index_type = table.column("sex").type.index_type

    assert output_columns == list(column_specs.keys())
    assert output_rows == results
    assert categories == ["M", "F", "I"]
    assert index_type == pyarrow.int8()
    assert table.column("patient_id").type == pyarrow.int64()
    assert table.column("year_of_birth").type == pyarrow.uint16()
