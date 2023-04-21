import random

import pytest

from ehrql.utils import regex_utils


@pytest.mark.parametrize(
    "re_str,examples",
    [
        # Branches
        (
            "abc(foo|bar)",
            ["abcbar", "abcfoo"],
        ),
        # Ranges
        (
            "[A-Z][0-9]",
            ["D1", "V1", "H0", "L9", "E2"],
        ),
        # Repeats
        (
            "A{2,4}_?B{2}",
            ["AAABB", "AABB", "AA_BB", "AABB", "AAA_BB"],
        ),
        # Unbounded repeats
        (
            "a+b*",
            ["aaaaaaaab", "ab", "aaaaaaaaaa", "aab", "aaaaaabbb"],
        ),
        # All together now ...
        (
            "(none|alpha[A-Z]{3,5}|digit[0-9]{3,5})",
            ["alphaCVD", "alphaALT", "alphaFAH", "none", "digit18445"],
        ),
    ],
)
def test_create_regex_generator(re_str, examples):
    generator = regex_utils.create_regex_generator(re_str)
    rnd = random.Random(1234)
    assert [generator(rnd) for _ in examples] == examples


def test_validate_regex():
    assert regex_utils.validate_regex("E[A-Z]{3}-(foo|bar)")


@pytest.mark.parametrize(
    "re_str,error",
    [
        # Parse errors from Python's regex engine are bubbled up
        ("abc(123", r"missing \), unterminated subpattern at position 3"),
        # Valid regexes which use unhandled constructs (e.g. non-greedy matches) should
        # raise an "unsupported" error
        ("t+?test", "unsupported"),
        # Subpattern groups are supported, but attempting to set flags inside the group
        # is not
        ("(?i:TEST)", "unsupported"),
        # And neither is unsetting flags
        ("(?-i:TEST)", "unsupported"),
    ],
)
def test_validate_regex_error(re_str, error):
    with pytest.raises(regex_utils.RegexError, match=error):
        regex_utils.validate_regex(re_str)
