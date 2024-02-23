from ehrql.file_formats.arrow import (
    ArrowRowsReader,
    write_rows_arrow,
)
from ehrql.file_formats.base import ValidationError
from ehrql.file_formats.csv import (
    CSVGZRowsReader,
    CSVRowsReader,
    write_rows_csv,
    write_rows_csv_gz,
)


FILE_FORMATS = {
    ".arrow": (write_rows_arrow, ArrowRowsReader),
    ".csv": (write_rows_csv, CSVRowsReader),
    ".csv.gz": (write_rows_csv_gz, CSVGZRowsReader),
}


def write_rows(filename, rows, column_specs):
    extension = get_file_extension(filename)
    writer = FILE_FORMATS[extension][0]
    # We use None for stdout
    if filename is not None:
        filename.parent.mkdir(parents=True, exist_ok=True)
    writer(filename, rows, column_specs)


def read_rows(filename, column_specs, allow_missing_columns=False):
    extension = get_file_extension(filename)
    if extension not in FILE_FORMATS:
        raise ValidationError(f"Unsupported file type: {extension}")
    if not filename.is_file():
        raise ValidationError(f"Missing file: {filename}")
    reader = FILE_FORMATS[extension][1]
    return reader(filename, column_specs, allow_missing_columns=allow_missing_columns)


def get_file_extension(filename):
    if filename is None:
        # If we have no filename we're writing to stdout, so default to CSV
        return ".csv"
    elif filename.suffix == ".gz":
        return "".join(filename.suffixes[-2:])
    else:
        return filename.suffix
