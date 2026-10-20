from ..tables import p


title = "Operations with bytes literals"

text = r"""
This section covers operations that are already documented in the "Operations on all series" chapter,
but extends them to usages where bytes values are supplied directly in ehrQL code.

In the tables, bytes are written as `\xab\xcd\xef`.
This is the same value that is written as `b"\xab\xcd\xef"` in Python and ehrQL code.
"""

table_data = {
    p: r"""
          |  by1
        --+------
        1 | \xab\xcd\xef
        2 | \x00
        3 |
        """,
}


def test_equals_fixed_literal_value(spec_test):
    spec_test(
        table_data,
        p.by1 == b"\xab\xcd\xef",
        {1: True, 2: False, 3: None},
    )


def test_not_equals_fixed_literal_value(spec_test):
    spec_test(
        table_data,
        p.by1 != b"\xab\xcd\xef",
        {1: False, 2: True, 3: None},
    )


def test_is_in_with_fixed_literal_values(spec_test):
    spec_test(
        table_data,
        p.by1.is_in([b"\xab\xcd\xef", b"\x00"]),
        {
            1: True,
            2: True,
            3: None,
        },
    )


def test_map_values_with_fixed_literal_values(spec_test):
    spec_test(
        table_data,
        p.by1.map_values(
            {
                b"\xab\xcd\xef": "a",
                b"\x00": "b",
            },
            default="c",
        ),
        {
            1: "a",
            2: "b",
            3: "c",
        },
    )
