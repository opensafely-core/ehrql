from ehrql.file_formats.arrow import (
    ArrowDatasetReader,
    write_dataset_arrow,
)
from ehrql.file_formats.base import ValidationError
from ehrql.file_formats.csv import (
    CSVDatasetReader,
    CSVGZDatasetReader,
    write_dataset_csv,
    write_dataset_csv_gz,
)


FILE_FORMATS = {
    ".arrow": (write_dataset_arrow, ArrowDatasetReader),
    ".csv": (write_dataset_csv, CSVDatasetReader),
    ".csv.gz": (write_dataset_csv_gz, CSVGZDatasetReader),
}


def write_dataset(filename, results, column_specs):
    extension = get_file_extension(filename)
    writer = FILE_FORMATS[extension][0]
    # We use None for stdout
    if filename is not None:
        filename.parent.mkdir(parents=True, exist_ok=True)
    writer(filename, results, column_specs)


def read_dataset(filename, column_specs):
    extension = get_file_extension(filename)
    if extension not in FILE_FORMATS:
        raise ValidationError(f"Unsupported file type: {extension}")
    if not filename.is_file():
        raise ValidationError(f"Missing file: {filename}")
    reader = FILE_FORMATS[extension][1]
    return reader(filename, column_specs)


def get_file_extension(filename):
    if filename is None:
        # If we have no filename we're writing to stdout, so default to CSV
        return ".csv"
    elif filename.suffix == ".gz":
        return "".join(filename.suffixes[-2:])
    else:
        return filename.suffix
