from ..tables import p


title = "Operations with bytes literals"

# TODO: Make this more readable
table_data = {
    p: r"""
          |  by1
        --+------
        1 | \xab\xcd\xef\x01\xab\xcd\xef\x01\xab\xcd\xef\x01\xab\xcd\xef\x01
        2 | \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        3 |
        """,
}


def test_equals_fixed_literal_value(spec_test):
    spec_test(
        table_data,
        p.by1 == b"\xab\xcd\xef\x01" * 4,
        {1: True, 2: False, 3: None},
    )


def test_not_equals_fixed_literal_value(spec_test):
    spec_test(
        table_data,
        p.by1 != b"\xab\xcd\xef\x01" * 4,
        {1: False, 2: True, 3: None},
    )
