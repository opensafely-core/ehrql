import textwrap
from io import StringIO
from pathlib import Path

import pytest

from . import test_complete_examples


# The SuperFences extension that we use has its own test suite.
# The tests below cover only the most common cases
# and are to help document and catch changes in behaviour
# that we may be interested in.
@pytest.mark.parametrize(
    "fence,expected_example",
    [
        pytest.param(
            textwrap.dedent(
                """\
                ```ehrql
                ```
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"),
                    fence_number=1,
                    source="",
                ),
            ],
            id="fence with no lines",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```ehrql
                some code
                ```
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"),
                    fence_number=1,
                    source="some code",
                ),
            ],
            id="fence with one line",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```ehrql
                some code
                more code
                ```
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"),
                    fence_number=1,
                    source="some code\nmore code",
                ),
            ],
            id="fence with multiple lines",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```ehrql
                some code
                ```ehrql
                more code
                ```
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"),
                    fence_number=1,
                    source="some code\n```ehrql\nmore code",
                ),
            ],
            id="open fence",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                some text
                ```ehrql
                some code
                ```
                more text
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"),
                    fence_number=1,
                    source="some code",
                ),
            ],
            id="fence between text",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```ehrql
                some code
                ```
                some text
                ```ehrql
                more code
                ```
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"), fence_number=1, source="some code"
                ),
                test_complete_examples.EhrqlExample(
                    path=Path("test"), fence_number=2, source="more code"
                ),
            ],
            id="multiple fences",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                > ```ehrql
                  some code
                  ```
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"), fence_number=1, source="some code"
                ),
            ],
            id="fence in quote",
        ),
        # List marker must be followed by a blank line with at least one space,
        # and the fence starts on next line.
        # Use an explicit newline character so that we can:
        # * keep the desired formatting
        # * avoid complaints from tooling about trailing whitespace
        pytest.param(
            textwrap.dedent(
                """\
                * \n
                  ```ehrql
                  some code
                  ```
                """
            ),
            [
                test_complete_examples.EhrqlExample(
                    path=Path("test"), fence_number=1, source="some code"
                ),
            ],
            id="fence in list",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```ehrql
                some code
                """
            ),
            [],
            id="fence at end of file",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```python
                some code
                ```
                """
            ),
            [],
            id="fence with non-matching syntax",
        ),
    ],
)
def test_find_docs_examples(fence, expected_example):
    example = StringIO(fence)
    # Unlike file objects, StringIO objects do not have a name.
    # In the relevant code being tested,
    # we access the file's name to save somewhat redundantly passing the name.
    example.name = "test"

    result = list(
        test_complete_examples.find_complete_ehrql_examples_in_markdown(example)
    )
    assert result == expected_example
