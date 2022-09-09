from databuilder.file_formats.csv import write_dataset_csv, write_dataset_csv_gz

FILE_FORMATS = {
    ".csv": write_dataset_csv,
    ".csv.gz": write_dataset_csv_gz,
}


def write_dataset(filename, results, column_specs):
    extension = get_file_extension(filename)
    writer = FILE_FORMATS[extension]
    # We use None for stdout
    if filename is not None:
        filename.parent.mkdir(parents=True, exist_ok=True)
    writer(filename, results, column_specs)


def get_file_extension(filename):
    if filename is None:
        # If we have no filename we're writing to stdout, so default to CSV
        return ".csv"
    elif filename.suffix == ".gz":
        return "".join(filename.suffixes[-2:])
    else:
        return filename.suffix
