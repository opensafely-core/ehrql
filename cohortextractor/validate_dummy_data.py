from datetime import datetime

import pandas as pd


SUPPORTED_FILE_FORMATS = ["csv", "csv.gz"]


class DummyDataValidationError(Exception):
    pass


def validate_dummy_data(column_definitions, dummy_data_file):
    """Validate that dummy data provided by user matches expected structure and format.

    Raises DummyDataValidationError if dummy data is not valid.
    """

    df = read_into_dataframe(dummy_data_file)
    validate_expected_columns(df, column_definitions)

    for col_name, query_node in column_definitions.items():
        if col_name == "population":
            # Ignore the population definition, since it is not used as a column in the
            # output
            continue

        validator = get_csv_validator(col_name, query_node)

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

    for ix, value in enumerate(df["patient_id"]):
        if not isinstance(value, int):
            raise DummyDataValidationError(
                f"Invalid value `{value!r}` for patient_id in row {ix + 2}"
            )


def read_into_dataframe(path):
    """Read data from path into a Pandas DataFrame."""

    try:
        if path.suffixes in [[".csv"], [".csv", ".gz"]]:
            return pd.read_csv(path)
        else:
            msg = f"Dummy data must be in one of the following formats: {', '.join(SUPPORTED_FILE_FORMATS)}"
            raise DummyDataValidationError(msg)
    except FileNotFoundError:
        raise DummyDataValidationError(f"Dummy data file not found: {path}")


def validate_expected_columns(df, columns_definitions):
    """Raise DummyDataValidationError if dataframe does not have expected columns."""
    expected_columns = {
        col_name
        for col_name in columns_definitions.keys()
        if not col_name == "population"
    }
    expected_columns.add("patient_id")

    extra_columns = set(df.columns) - expected_columns
    if extra_columns:
        if len(extra_columns) == 1:
            msg = f"Unexpected column in dummy data: {list(extra_columns)[0]}"
        else:
            msg = f"Unexpected columns in dummy data: {', '.join(extra_columns)}"
        raise DummyDataValidationError(msg)

    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        if len(missing_columns) == 1:
            msg = f"Missing column in dummy data: {list(missing_columns)[0]}"
        else:
            msg = f"Missing columns in dummy data: {', '.join(missing_columns)}"
        raise DummyDataValidationError(msg)


def get_csv_validator(col_name, query_node):
    """Return function that validates that value is valid to appear in column.

    A validator is a single-argument function that raises a ValueError on invalid input.
    """

    def bool_validator(value):
        if value not in [True, False]:
            raise ValueError

    def date_validator_date_or_datetime(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    # We don't yet track column types so we can only do some cursory validation based on
    # known column names and aggregation functions
    columns_to_validator_mapping = {
        "date": date_validator_date_or_datetime,
        "date_start": date_validator_date_or_datetime,
        "date_end": date_validator_date_or_datetime,
        "date_of_birth": date_validator_date_or_datetime,
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
        hasattr(query_node, "column")
        and query_node.column in columns_to_validator_mapping
    ):
        return columns_to_validator_mapping[query_node.column]
    if (
        hasattr(query_node, "function")
        and query_node.function in functions_to_validator_mapping
    ):
        return functions_to_validator_mapping[query_node.function]
    return str
