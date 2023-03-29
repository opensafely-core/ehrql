import os

from databuilder.file_formats.arrow import (
    read_dataset_arrow,
    validate_dataset_arrow,
    write_dataset_arrow,
)
from databuilder.file_formats.csv import (
    read_dataset_csv,
    read_dataset_csv_gz,
    validate_dataset_csv,
    validate_dataset_csv_gz,
    write_dataset_csv,
    write_dataset_csv_gz,
)
from databuilder.file_formats.validation import ValidationError

FILE_FORMATS = {
    ".arrow": (write_dataset_arrow, validate_dataset_arrow, read_dataset_arrow),
    ".csv": (write_dataset_csv, validate_dataset_csv, read_dataset_csv),
    ".csv.gz": (write_dataset_csv_gz, validate_dataset_csv_gz, read_dataset_csv_gz),
}


def write_dataset(filename, results, column_specs):
    extension = get_file_extension(filename)
    writer = get_methods(extension)[0]
    # We use None for stdout
    if filename is not None:
        filename.parent.mkdir(parents=True, exist_ok=True)
    writer(filename, results, column_specs)


def validate_dataset(filename, column_specs):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"{filename} not found")
    extension = get_file_extension(filename)
    validator = get_methods(extension)[1]
    validator(filename, column_specs)


def read_dataset(filename, column_specs):
    extension = get_file_extension(filename)
    reader = get_methods(extension)[2]
    return reader(filename, column_specs)


def validate_file_types_match(dummy_filename, output_filename):
    if get_file_extension(dummy_filename) != get_file_extension(output_filename):
        raise ValidationError(
            f"Dummy data file does not have the same file extension as the output "
            f"filename:\n"
            f"Dummy data file: {dummy_filename}\n"
            f"Output file: {output_filename}"
        )


def get_file_extension(filename):
    if filename is None:
        # If we have no filename we're writing to stdout, so default to CSV
        return ".csv"
    elif filename.suffix == ".gz":
        return "".join(filename.suffixes[-2:])
    else:
        return filename.suffix


def get_methods(extension):
    if extension == ".feather":
        extension = ".arrow"
    if extension not in FILE_FORMATS:
        raise ValueError(f"Loading from {extension} files not supported")
    return FILE_FORMATS[extension]
