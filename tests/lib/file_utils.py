import csv
import gzip

from pyarrow.feather import read_table

from ehrql.file_formats import get_file_extension


def read_file_as_dicts(filename):
    extension = get_file_extension(filename)
    if extension == ".csv":
        with open(filename, newline="") as f:
            return list(csv.DictReader(f))
    elif extension == ".csv.gz":
        with gzip.open(filename, "rt", newline="") as f:
            return list(csv.DictReader(f))
    elif extension == ".arrow":
        return read_table(str(filename)).to_pylist()
    else:
        assert False, f"Unsupported extension: {filename}"
