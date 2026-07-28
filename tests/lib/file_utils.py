import csv
import gzip

from pyarrow.ipc import open_file

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
        return open_file(str(filename)).read_all().to_pylist()
    else:
        assert False, f"Unsupported extension: {filename}"
