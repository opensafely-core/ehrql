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


def test_is_in_with_fixed_literal_values(spec_test):
    spec_test(
        table_data,
        p.by1.is_in([b"\xab\xcd\xef\x01" * 4, b"\x00" * 16]),
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
                b"\xab\xcd\xef\x01" * 4: "a",
                b"\x00" * 16: "b",
            },
            default="c",
        ),
        {
            1: "a",
            2: "b",
            3: "c",
        },
    )
