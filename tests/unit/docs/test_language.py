import pytest

from ehrql.docs.language import is_included_attr
from ehrql.utils.docs_utils import exclude_from_docs


class Example:
    some_attr = "some_value"

    def some_method(self):
        raise NotImplementedError()

    @property
    def some_property(self):
        raise NotImplementedError()

    def _some_internal_method(self):
        raise NotImplementedError()

    @exclude_from_docs
    def some_excluded_method(self):
        raise NotImplementedError()


@pytest.mark.parametrize(
    "name,expected",
    [
        ("some_attr", False),
        ("some_method", True),
        ("some_property", True),
        ("_some_internal_method", False),
        ("some_excluded_method", False),
    ],
)
def test_is_included_attr(name, expected):
    value = getattr(Example, name)
    assert is_included_attr(name, value) == expected
