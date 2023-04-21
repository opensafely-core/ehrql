import pytest

from ehrql.file_formats.validation import ValidationError, validate_columns


def test_validate_columns():
    # Column order is not significant, neither is the presence of additional columns so
    # long as all required columns are present
    validate_columns(["a", "b", "c", "d"], ["c", "b", "a"])
    with pytest.raises(ValidationError, match="Missing columns: b, d"):
        validate_columns(["c", "a"], ["a", "b", "c", "d"])
