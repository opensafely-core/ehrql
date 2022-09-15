import csv
import datetime
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
    format_row = create_row_formatter(column_specs.values())
    writer = csv.writer(fileobj)
    writer.writerow(headers)
    writer.writerows(map(format_row, results))


def create_row_formatter(column_specs):
    formatters = [create_column_formatter(spec) for spec in column_specs]
    return lambda row: [f(value) for f, value in zip(formatters, row)]


def create_column_formatter(spec):
    # Most types naturally format themselves as we'd like in CSV
    if spec.type in (int, float, str, datetime.date):
        return identity
    # But we need special handling for booleans
    elif spec.type is bool:
        return format_bool
    else:
        assert False, f"Unhandled type: {spec.type}"


def identity(value):
    return value


def format_bool(value):
    if value is None:
        return ""
    return "1" if value else "0"
