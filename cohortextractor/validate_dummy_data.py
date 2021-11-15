from datetime import datetime

import pandas as pd

from .query_language import ValueFromRow
from .query_utils import get_column_definitions


SUPPORTED_FILE_FORMATS = ["csv", "csv.gz"]


class DummyDataValidationError(Exception):
    pass


def validate_dummy_data(cohort_class, dummy_data_file, output_file):
    """Validate that dummy data provided by user matches expected structure and format.

    Raises DummyDataValidationError if dummy data is not valid.
    """

    validate_file_extension(output_file, dummy_data_file)

    df = read_into_dataframe(dummy_data_file)

    column_definitions = get_column_definitions(cohort_class)

    # Ignore the population definition, since it is not used as a column in the output
    column_definitions.pop("population", None)
    # Add in the patient_id, which is always included as a column in the output
    column_definitions["patient_id"] = ValueFromRow(source=None, column="patient_id")

    validate_expected_columns(df, column_definitions)

    validate_column_values(df, column_definitions)


def validate_file_extension(output_file, dummy_data_file):
    """Raise DummyDataValidationError if dummy data file does not have expected file extension."""
    if output_file.suffixes != dummy_data_file.suffixes:
        expected_extension = "".join(output_file.suffixes)
        msg = f"Expected dummy data file with extension {expected_extension}; got {dummy_data_file.name}"
        raise DummyDataValidationError(msg)


def read_into_dataframe(path):
    """Read data from path into a Pandas DataFrame."""
    try:
        suffixes = ".".join([suffix.strip(".") for suffix in path.suffixes])
        assert suffixes in SUPPORTED_FILE_FORMATS
        return pd.read_csv(path)
    except FileNotFoundError:
        raise DummyDataValidationError(f"Dummy data file not found: {path}")


def validate_expected_columns(df, columns_definitions):
    """Raise DummyDataValidationError if dataframe does not have expected columns."""
    expected_columns = set(columns_definitions.keys())
    extra_columns = set(df.columns) - expected_columns
    if extra_columns:
        raise DummyDataValidationError(
            f"Unexpected columns in dummy data: {', '.join(extra_columns)}"
        )

    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        raise DummyDataValidationError(
            f"Missing columns in dummy data: {', '.join(missing_columns)}"
        )


def validate_column_values(df, column_definitions):
    """Raise DummyDataValidationError if dataframe columns contains values of unexpected types."""
    for col_name, query_node in column_definitions.items():
        validator = get_csv_validator(query_node)
        for ix, value in enumerate(df[col_name]):

            if pd.isna(value) or not value:
                # Ignore null or missing values
                continue

            try:
                validator(value)
            except ValueError:
                raise DummyDataValidationError(
                    f"Invalid value `{value!r}` for {col_name} in row {ix + 2}"
                )


def get_csv_validator(query_node):
    """Return function that validates that value is valid to appear in column.

    A validator is a single-argument function that raises a ValueError on invalid input.
    """

    def bool_validator(value):
        if value not in [True, False]:
            raise ValueError

    def date_validator(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    # We don't yet track column types so we can only do some cursory validation based on
    # known column names and aggregation functions
    columns_to_validator_mapping = {
        "date": date_validator,
        "date_start": date_validator,
        "date_end": date_validator,
        "date_of_birth": date_validator,
        "patient_id": int,
        "pseudo_id": int,
        "numeric_value": float,
        "positive_result": bool_validator,
        "index_of_multiple_deprivation_rounded": int,
    }
    functions_to_validator_mapping = {
        "exists": bool_validator,
        "count": int,
    }
    if (
        hasattr(query_node, "function")
        and query_node.function in functions_to_validator_mapping
    ):
        return functions_to_validator_mapping[query_node.function]
    if (
        hasattr(query_node, "column")
        and query_node.column in columns_to_validator_mapping
    ):
        return columns_to_validator_mapping[query_node.column]
    return str
