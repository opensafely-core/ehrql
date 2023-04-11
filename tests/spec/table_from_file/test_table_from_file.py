from pathlib import Path

from databuilder.file_formats import FILE_FORMATS, write_dataset
from databuilder.query_model.column_specs import ColumnSpec
from databuilder.tables import PatientFrame, Series, table_from_file

from ..tables import p


title = "Defining a table from a file"

table_data = {
    p: """
          | i1
        --+----
        1 | 10
        2 | 20
        3 | 30
        """,
}

FIXTURE_DIR = Path(__file__).parent


def write_fixture_files():  # pragma: no cover
    """
    python -c 'from tests.spec.table_from_file.test_table_from_file import write_fixture_files; write_fixture_files()'
    """
    file_data = [
        (1, 100),
        (3, 300),
    ]
    column_specs = {"patient_id": ColumnSpec(int), "n": ColumnSpec(int)}
    for extension in FILE_FORMATS.keys():
        filename = FIXTURE_DIR / f"test_file{extension}"
        write_dataset(filename, file_data, column_specs)


def test_table_from_file_csv(spec_test):
    @table_from_file(FIXTURE_DIR / "test_file.csv")
    class t(PatientFrame):
        n = Series(int)

    spec_test(
        table_data,
        p.i1 + t.n,
        {
            1: 10 + 100,
            2: None,
            3: 30 + 300,
        },
    )


def test_table_from_file_csv_gz(spec_test):
    @table_from_file(FIXTURE_DIR / "test_file.csv.gz")
    class t(PatientFrame):
        n = Series(int)

    spec_test(
        table_data,
        p.i1 + t.n,
        {
            1: 10 + 100,
            2: None,
            3: 30 + 300,
        },
    )


def test_table_from_file_feather(spec_test):
    @table_from_file(FIXTURE_DIR / "test_file.arrow")
    class t(PatientFrame):
        n = Series(int)

    spec_test(
        table_data,
        p.i1 + t.n,
        {
            1: 10 + 100,
            2: None,
            3: 30 + 300,
        },
    )
