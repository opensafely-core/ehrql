import csv
import datetime
import gzip
import sys
from contextlib import nullcontext

from databuilder.file_formats.validation import ValidationError, validate_headers


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


def validate_dataset_csv(filename, column_specs):
    with open(filename, newline="") as f:
        # Consume the generator to raise any errors
        for _ in read_dataset_csv_lines(f, column_specs):
            pass


def validate_dataset_csv_gz(filename, column_specs):
    with gzip.open(filename, "rt", newline="") as f:
        # Consume the generator to raise any errors
        for _ in read_dataset_csv_lines(f, column_specs):
            pass


def read_dataset_csv_lines(lines, column_specs):
    reader = csv.reader(lines)
    headers = next(reader)
    validate_headers(headers, list(column_specs.keys()))
    row_parser = create_row_parser(headers, column_specs)
    for n, row in enumerate(reader, start=1):
        try:
            yield row_parser(row)
        except ValueError as e:
            raise ValidationError(f"row {n}: {e}")


def create_row_parser(headers, column_specs):
    parsers = [
        create_column_parser(headers, name, spec) for name, spec in column_specs.items()
    ]
    headers_len = len(headers)

    def row_parser(row):
        if len(row) != headers_len:
            raise ValueError(f"expected {headers_len} columns but got {len(row)}")
        return tuple(parser(row) for parser in parsers)

    return row_parser


def create_column_parser(headers, name, spec):

    if spec.type in (int, float, str):
        convertor = spec.type
    elif spec.type is datetime.date:
        convertor = datetime.date.fromisoformat
    elif spec.type is bool:
        convertor = parse_bool
    else:
        assert False, f"Unhandled type: {spec.type}"

    index = headers.index(name)

    def parser(row):
        value = row[index]
        # We use empty string to encode None. This means we are unable to distinguish
        # the empty string from None in string-typed columns. This is just fundamental
        # limitation of CSV as a format.
        if value == "":
            if not spec.nullable:
                raise ValueError(f"NULL value in non-nullable column '{name}'")
            return None

        try:
            return convertor(value)
        except ValueError as e:
            raise ValueError(f"column {name!r}: {e}")

    return parser


def parse_bool(value):
    if value == "1":
        return True
    elif value == "0":
        return False
    else:
        raise ValueError("invalid boolean, must be '0' or '1'")
