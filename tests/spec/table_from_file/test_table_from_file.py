import csv
import gzip

import pyarrow
from pyarrow.feather import write_feather

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

file_data = [
    (1, 100),
    (3, 300),
]


def test_table_from_file_csv(spec_test, tmp_path):
    path = tmp_path / "test_table_from_file.csv"
    with path.open("w") as f:
        writer = csv.writer(f)
        writer.writerow(["patient_id", "n"])
        writer.writerows(file_data)

    @table_from_file(path)
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


def test_table_from_file_csv_gz(spec_test, tmp_path):
    path = tmp_path / "test_table_from_file.csv.gz"
    with gzip.open(path, "wt", newline="", compresslevel=6) as f:
        writer = csv.writer(f)
        writer.writerow(["patient_id", "n"])
        writer.writerows(file_data)

    @table_from_file(path)
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


def test_table_from_file_feather(spec_test, tmp_path):
    path = tmp_path / "test_table_from_file.feather"

    columns = ["patient_id", "n"]
    table = pyarrow.Table.from_pylist([dict(zip(columns, f)) for f in file_data])
    write_feather(table, str(path), compression="zstd")

    @table_from_file(path)
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
