import pytest

from databuilder.file_formats.validation import (
    ValidationError,
    validate_columns,
    validate_headers,
)


@pytest.mark.parametrize(
    "headers,error",
    [
        (["foo", "bar", "baz"], None),
        (["foo", "baz"], r"Missing columns"),
        (["foo", "bar", "baz", "boo"], r"Unexpected columns"),
        (["bar", "baz", "boo"], r"Missing columns[\s\S]*Unexpected columns"),
        (["foo", "baz", "bar"], r"Headers not in expected order"),
    ],
)
def test_validate_headers(headers, error):
    expected = ["foo", "bar", "baz"]
    if error is None:
        validate_headers(headers, expected)
    else:
        with pytest.raises(ValidationError, match=error):
            validate_headers(headers, expected)


def test_validate_columns():
    # Column order is not significant, neither is the presence of additional columns so
    # long as all required columns are present
    validate_columns(["a", "b", "c", "d"], ["c", "b", "a"])
    with pytest.raises(ValidationError, match="Missing columns: b, d"):
        validate_columns(["c", "a"], ["a", "b", "c", "d"])
