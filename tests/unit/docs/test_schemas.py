import pytest

from ehrql.docs.schemas import get_table_docstring
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
