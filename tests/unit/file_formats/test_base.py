import pytest

from ehrql.file_formats.base import ValidationError, validate_columns
from ehrql.query_model.column_specs import ColumnSpec


def test_validate_columns():
    # Column order is not significant, neither is the presence of additional columns so
    # long as all required columns are present
    validate_columns(
        ["a", "b", "c", "d"],
        {
            "c": ColumnSpec(int),
            "b": ColumnSpec(int),
            "a": ColumnSpec(int),
        },
    )


def test_validate_columns_fails_on_missing_columns_by_default():
    with pytest.raises(ValidationError, match="Missing columns: b, d"):
        validate_columns(
            ["c", "a"],
            {
                "a": ColumnSpec(int),
                "b": ColumnSpec(int),
                "c": ColumnSpec(int),
                "d": ColumnSpec(int),
            },
        )


def test_validate_columns_allows_missing_columns():
    validate_columns(
        ["c", "a"],
        {
            "a": ColumnSpec(int),
            "b": ColumnSpec(int),
            "c": ColumnSpec(int),
        },
        allow_missing_columns=True,
    )


def test_validate_columns_does_not_allow_missing_nonnullable_columns():
    with pytest.raises(ValidationError, match="Missing columns: b"):
        validate_columns(
            ["c", "a"],
            {
                "a": ColumnSpec(int),
                "b": ColumnSpec(int, nullable=False),
                "c": ColumnSpec(int),
            },
            allow_missing_columns=True,
        )
