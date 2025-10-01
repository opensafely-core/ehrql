import pytest

from ehrql.docs.schemas import build_table, get_table_docstring
from ehrql.tables import EventFrame, Series, table


def test_get_table_docstring():
    @table
    class parent_table(EventFrame):
        "I have a docstring"

        col_a = Series(str)

    @table
    class child_table(parent_table.__class__):
        """
        I have a docstring

        With some extra stuff
        """

        col_b = Series(str)

    assert (
        get_table_docstring(child_table.__class__)
        == "I have a docstring\n\nWith some extra stuff"
    )


def test_get_table_docstring_with_mismatch():
    @table
    class parent_table(EventFrame):
        "I have a docstring"

        col_a = Series(str)

    @table
    class child_table(parent_table.__class__):
        "I have a different docstring"

        col_b = Series(str)

    with pytest.raises(ValueError):
        get_table_docstring(child_table.__class__)


def test_missing_reference_to_required_permission():
    @table
    class some_table(EventFrame):
        "Some docstring"

        class _meta:
            required_permission = "special"

        col_a = Series(str)

    with pytest.raises(
        ValueError, match="doesn't include '`special` permission' in its docstring"
    ):
        build_table("some_table", some_table)
