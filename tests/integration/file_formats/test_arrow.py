import pyarrow.feather
import pytest

from ehrql.file_formats import write_dataset
from ehrql.query_model.column_specs import ColumnSpec


def test_write_dataset_arrow(tmp_path):
    filename = tmp_path / "somedir" / "file.arrow"
    column_specs = {
        "patient_id": ColumnSpec(int),
        "year_of_birth": ColumnSpec(int, min_value=1900, max_value=2100),
        "sex": ColumnSpec(str, categories=("M", "F", "I")),
        "risk_score": ColumnSpec(float, categories=(0.0, 0.5, 1.0)),
    }
    results = [
        (123, 1980, "F", 0.0),
        (456, None, None, 0.5),
        (789, 1999, "M", 1.0),
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
    # This column has categories, but it's not a string so we shouldn't encode it as a
    # dictionary
    assert not pyarrow.types.is_dictionary(table.column("risk_score").type)


def test_write_dataset_arrow_annotates_errors_with_column(tmp_path):
    filename = tmp_path / "file.arrow"
    column_specs = {
        "value": ColumnSpec(int, min_value=0, max_value=100),
    }
    results = [(-1,)]
    with pytest.raises(OverflowError) as exc:
        write_dataset(filename, results, column_specs)
    assert "Error when writing column 'value'" in exc.value.__notes__


def test_write_dataset_arrow_raises_helpful_dictionary_errors(tmp_path):
    filename = tmp_path / "file.arrow"
    column_specs = {
        "category": ColumnSpec(str, categories=("A", "B", "C")),
    }
    results = [("D",)]
    with pytest.raises(
        ValueError,
        match="Invalid value 'D' for column 'category'\nAllowed are: 'A', 'B', 'C'",
    ):
        write_dataset(filename, results, column_specs)
