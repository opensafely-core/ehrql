import datetime

import pytest

from ehrql.file_formats import (
    FILE_FORMATS,
    ValidationError,
    read_dataset,
    write_dataset,
)
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.sqlalchemy_types import TYPE_MAP


TEST_FILE_SPECS = {
    "patient_id": ColumnSpec(int),
    "b": ColumnSpec(bool),
    "i": ColumnSpec(int),
    "f": ColumnSpec(float),
    "s": ColumnSpec(str),
    "c": ColumnSpec(str, categories=("A", "B")),
    "d": ColumnSpec(datetime.date),
}

TEST_FILE_DATA = [
    (123, True, 1, 2.3, "a", "A", datetime.date(2020, 1, 1)),
    (456, False, -5, -0.4, "b", "B", datetime.date(2022, 12, 31)),
    (789, None, None, None, None, None, None),
]


def test_all_types_are_covered_in_test():
    types = [spec.type for spec in TEST_FILE_SPECS.values()]
    assert set(types) == set(TYPE_MAP)


# Generate a test file for each of the file formats we support. This is a session-scoped
# fixture so we generate each file once and then use it across multiple tests.
@pytest.fixture(params=list(FILE_FORMATS.keys()), scope="session")
def test_file(request, tmp_path_factory):
    # We have to use `tmp_path_factory` rather than the usual `tmp_path` because the latter
    # is function-scoped and we need a session-scoped fixture
    tmp_path = tmp_path_factory.mktemp("test_file_formats")
    extension = request.param
    filename = tmp_path / f"dataset{extension}"
    write_dataset(filename, TEST_FILE_DATA, TEST_FILE_SPECS)
    yield filename


def test_read_and_write_dataset_roundtrip(test_file):
    # Basic test that we can read what we've written
    with read_dataset(test_file, TEST_FILE_SPECS) as reader:
        results = list(reader)
    assert results == TEST_FILE_DATA


def test_read_dataset_with_a_subset_of_columns(test_file):
    # Read a subset of the original columns and in a different order
    column_specs = {
        "patient_id": ColumnSpec(int),
        "s": ColumnSpec(str),
        "i": ColumnSpec(int),
    }
    with read_dataset(test_file, column_specs) as reader:
        results = list(reader)

    original_columns = list(TEST_FILE_SPECS.keys())
    patient_id_index = original_columns.index("patient_id")
    s_index = original_columns.index("s")
    i_index = original_columns.index("i")
    expected = [
        (row[patient_id_index], row[s_index], row[i_index]) for row in TEST_FILE_DATA
    ]

    assert results == expected


def test_read_dataset_can_be_iterated_multiple_times(test_file):
    with read_dataset(test_file, TEST_FILE_SPECS) as reader:
        # Each time we iterate `reader` we should get the full contents of the file
        results_1 = list(reader)
        results_2 = list(reader)
    assert results_1 == TEST_FILE_DATA
    assert results_2 == TEST_FILE_DATA


def test_read_dataset_validates_on_open(test_file):
    # We should get a ValidationEror (because the columns don't match) immediately on
    # opening the file, even if we don't try to read any rows from it
    with pytest.raises(ValidationError):
        read_dataset(test_file, {"wrong_column": ColumnSpec(int)})


def test_read_dataset_validates_columns(test_file):
    # Create a copy of the column specs with extra columns
    column_specs = TEST_FILE_SPECS.copy()
    column_specs["extra_column_1"] = ColumnSpec(int)
    column_specs["extra_column_2"] = ColumnSpec(int)

    with pytest.raises(
        ValidationError,
        match=("Missing columns: extra_column_1, extra_column_2"),
    ):
        read_dataset(test_file, column_specs)


def test_read_dataset_validates_types(test_file):
    # Create a copy of the column specs with a modified column type
    column_specs = TEST_FILE_SPECS.copy()
    column_specs["s"] = ColumnSpec(int)

    # The errors are different here because with Arrow we can validate the schema but
    # with CSV we can only validate individual values
    errors = {
        "dataset.arrow": "expected <class 'int'>, got string",
        "dataset.csv": "invalid literal for int",
        "dataset.csv.gz": "invalid literal for int",
    }

    with pytest.raises(ValidationError, match=errors[test_file.name]):
        read_dataset(test_file, column_specs)


def test_read_dataset_validates_categories(test_file):
    # Create a copy of the column specs with modified column categories
    column_specs = TEST_FILE_SPECS.copy()
    column_specs["c"] = ColumnSpec(str, categories=("X", "Y"))

    # The errors are different here because with Arrow we can validate the categories in
    # the schema but with CSV we can only validate individual values
    errors = {
        "dataset.arrow": (
            "Unexpected categories in column 'c'\n"
            "  Categories: A, B\n"
            "  Expected: X, Y"
        ),
        "dataset.csv": "'A' not in valid categories: 'X', 'Y'",
        "dataset.csv.gz": "'A' not in valid categories: 'X', 'Y'",
    }

    with pytest.raises(ValidationError, match=errors[test_file.name]):
        read_dataset(test_file, column_specs)


def test_read_dataset_validates_categories_on_non_categorical_column(test_file):
    # This tests that categories are validated even if an arrow column is not
    # categorical. This is relevant if a user provides their own dummy dataset without
    # making the columns categorical.

    if test_file.suffix != ".arrow":
        pytest.skip("only relevant for arrow files")

    # Create a copy of the column specs with modified column categories
    column_specs = TEST_FILE_SPECS.copy()
    column_specs["s"] = ColumnSpec(str, categories=("X", "Y"))

    error = (
        "Unexpected categories in column 's'\n"
        "  Categories: a, b\n"
        "  Expected: X, Y"
    )

    with pytest.raises(ValidationError, match=error):
        read_dataset(test_file, column_specs)


def test_read_dataset_accepts_subset_of_expected_categories(test_file):
    # Create a copy of the column specs with an extra category on the categorical column
    # and the categories in a different order
    column_specs = TEST_FILE_SPECS.copy()
    column_specs["c"] = ColumnSpec(str, categories=("C", "B", "A"))

    # Check we can still read it correctly
    reader = read_dataset(test_file, column_specs)
    assert list(reader) == TEST_FILE_DATA


def test_dataset_readers_identity(test_file):
    reader_1 = read_dataset(test_file, TEST_FILE_SPECS)
    reader_2 = read_dataset(test_file, TEST_FILE_SPECS)
    reader_3 = read_dataset(test_file, {"i": ColumnSpec(int)})
    assert reader_1 == reader_2
    assert hash(reader_1) == hash(reader_2)
    assert reader_1 != reader_3
    # Cover the type-mismatch branch
    assert reader_1 != "foo"


def test_dataset_reader_repr(test_file):
    reader = read_dataset(test_file, TEST_FILE_SPECS)
    assert repr(test_file) in repr(reader)
