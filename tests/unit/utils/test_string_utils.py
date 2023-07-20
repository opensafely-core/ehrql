import pytest

from ehrql.utils.string_utils import strip_indent


@pytest.mark.parametrize(
    "s,expected",
    [
        (
            "Should\nbe\nuntouched",
            "Should\nbe\nuntouched",
        ),
        (
            """
            Leading newline and indent should be stripped:

              But nested indent retained

            Like this.
            """,
            (
                "Leading newline and indent should be stripped:\n"
                "\n"
                "  But nested indent retained\n"
                "\n"
                "Like this."
            ),
        ),
    ],
)
def test_strip_indent(s, expected):
    assert strip_indent(s) == expected
