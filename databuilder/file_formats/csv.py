import csv
import gzip
import sys
from contextlib import nullcontext


def write_dataset_csv(filename, results, column_specs):
    if filename is None:
        context = nullcontext(sys.stdout)
    else:
        # Set `newline` as per Python docs:
        # https://docs.python.org/3/library/csv.html#id3
        context = filename.open(mode="w", newline="")
    with context as f:
        write_dataset_csv_lines(f, results, column_specs)


def write_dataset_csv_gz(filename, results, column_specs):
    # Set `newline` as per Python docs: https://docs.python.org/3/library/csv.html#id3
    with gzip.open(filename, "wt", newline="", compresslevel=6) as f:
        write_dataset_csv_lines(f, results, column_specs)


def write_dataset_csv_lines(fileobj, results, column_specs):
    headers = list(column_specs.keys())
    writer = csv.writer(fileobj)
    writer.writerow(headers)
    writer.writerows(results)
