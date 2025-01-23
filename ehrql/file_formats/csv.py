import csv
import datetime
import gzip

from ehrql.file_formats.base import (
    BaseRowsReader,
    FileValidationError,
    validate_columns,
)


def write_rows_csv(filename, rows, column_specs):
    # Set `newline` as per Python docs: https://docs.python.org/3/library/csv.html#id3
    with filename.open(mode="w", newline="") as f:
        write_rows_csv_lines(f, rows, column_specs)


def write_rows_csv_gz(filename, rows, column_specs):
    # Set `newline` as per Python docs: https://docs.python.org/3/library/csv.html#id3
    with gzip.open(filename, "wt", newline="", compresslevel=6) as f:
        write_rows_csv_lines(f, rows, column_specs)


def write_rows_csv_lines(fileobj, rows, column_specs):
    headers = list(column_specs.keys())
    format_row = create_row_formatter(column_specs.values())
    writer = csv.writer(fileobj)
    writer.writerow(headers)
    writer.writerows(map(format_row, rows))


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
    return "T" if value else "F"


class BaseCSVRowsReader(BaseRowsReader):
    def _validate_basic(self):
        # CSV being what it is we can't properly validate the types it contains without
        # reading the entire thing, which we don't want do. So we read the first 10 rows
        # in the hope that if there's a type mismatch it will show up here.
        for _ in zip(self, range(10)):
            pass

    def __iter__(self):
        self._fileobj.seek(0)
        reader = csv.reader(self._fileobj)
        headers = next(reader)
        validate_columns(
            headers, self.column_specs, allow_missing_columns=self.allow_missing_columns
        )
        row_parser = create_row_parser(headers, self.column_specs)
        for n, row in enumerate(reader, start=1):
            try:
                yield row_parser(row)
            except ValueError as e:
                raise FileValidationError(f"row {n}: {e}")

    def close(self):
        self._fileobj.close()


class CSVRowsReader(BaseCSVRowsReader):
    def _open(self):
        self._fileobj = open(self.filename, newline="")


class CSVGZRowsReader(BaseCSVRowsReader):
    def _open(self):
        self._fileobj = gzip.open(self.filename, "rt", newline="")


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
    # Missing columns always return a NULL value
    if name not in headers:
        return lambda _: None

    if spec.type in (int, float, str):
        convertor = spec.type
    elif spec.type is datetime.date:
        convertor = datetime.date.fromisoformat
    elif spec.type is bool:
        convertor = parse_bool
    else:
        assert False, f"Unhandled type: {spec.type}"

    if spec.categories is not None:
        convertor = validate_categories(convertor, spec.categories)

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
    if value == "T":
        return True
    elif value == "F":
        return False
    else:
        raise ValueError("invalid boolean, must be 'T' or 'F'")


def validate_categories(convertor, categories):
    category_set = frozenset(categories)
    category_str = ", ".join(map(repr, categories))

    def wrapper(value):
        parsed = convertor(value)
        if parsed not in category_set:
            raise ValueError(f"{value!r} not in valid categories: {category_str}")
        return parsed

    return wrapper
