import os

from databuilder.file_formats.arrow import (
    ArrowDatasetReader,
    validate_dataset_arrow,
    write_dataset_arrow,
)
from databuilder.file_formats.csv import (
    CSVDatasetReader,
    validate_dataset_csv,
    validate_dataset_csv_gz,
    write_dataset_csv,
    write_dataset_csv_gz,
)
from databuilder.file_formats.validation import ValidationError


FILE_FORMATS = {
    ".arrow": (
        write_dataset_arrow,
        validate_dataset_arrow,
        ArrowDatasetReader,
    ),
    ".csv": (
        write_dataset_csv,
        validate_dataset_csv,
        CSVDatasetReader.from_csv,
    ),
    ".csv.gz": (
        write_dataset_csv_gz,
        validate_dataset_csv_gz,
        CSVDatasetReader.from_csv_gz,
    ),
}


def write_dataset(filename, results, column_specs):
    extension = get_file_extension(filename)
    writer = FILE_FORMATS[extension][0]
    # We use None for stdout
    if filename is not None:
        filename.parent.mkdir(parents=True, exist_ok=True)
    writer(filename, results, column_specs)


def validate_dataset(filename, column_specs):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"{filename} not found")
    extension = get_file_extension(filename)
    if extension not in FILE_FORMATS:
        raise ValueError(f"Loading from {extension} files not supported")
    validator = FILE_FORMATS[extension][1]
    validator(filename, column_specs)


def read_dataset(filename, column_specs):
    extension = get_file_extension(filename)
    if extension not in FILE_FORMATS:
        raise ValidationError(f"Unsupported file type: {extension}")
    if not os.path.isfile(filename):
        raise ValidationError(f"Missing file: {filename}")
    reader = FILE_FORMATS[extension][2]
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
