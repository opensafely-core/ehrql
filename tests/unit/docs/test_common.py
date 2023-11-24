import pytest

from ehrql.docs.common import get_docstring, get_function_body


class ExampleClass:
    # Comments above
    @staticmethod
    def example_method_with_docstring(
        arg1: int,
        arg2: str,
    ) -> str:  # pragma: no cover
        """
        Docstring goes here
        """
        # Make it bigger
        arg1 = arg1 + 100
        # Make it smaller
        arg1 = arg1 // 2
        return arg2 + str(arg1)

    def example_method_no_docstring(self):  # pragma: no cover
        # Return the thing
        return "foo"


EXPECTED_WITH_DOCSTRING = """\
# Make it bigger
arg1 = arg1 + 100
# Make it smaller
arg1 = arg1 // 2
return arg2 + str(arg1)
"""


EXPECTED_NO_DOCSTRING = """\
# Return the thing
return "foo"
"""


@pytest.mark.parametrize(
    "method,expected",
    [
        (ExampleClass.example_method_with_docstring, EXPECTED_WITH_DOCSTRING),
        (ExampleClass.example_method_no_docstring, EXPECTED_NO_DOCSTRING),
    ],
)
def test_get_function_body(method, expected):
    assert get_function_body(method) == expected


def test_get_docstring():
    assert (
        get_docstring(ExampleClass.example_method_with_docstring)
        == "Docstring goes here"
    )


def test_get_docstring_with_default():
    assert (
        get_docstring(ExampleClass.example_method_no_docstring, default="foo") == "foo"
    )


def test_get_docstring_with_error():
    with pytest.raises(ValueError, match="No docstring defined for public object"):
        get_docstring(ExampleClass.example_method_no_docstring)
