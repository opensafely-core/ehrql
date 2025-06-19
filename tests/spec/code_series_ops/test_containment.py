from ehrql.codes import codelist_from_csv_lines

from ..tables import p


title = "Testing for containment using codes"

table_data = {
    p: """
          |   c1
        --+--------
        1 | 123000
        2 | 456000
        3 | 789000
        4 |
        """,
}


def test_is_in(spec_test):
    spec_test(
        table_data,
        p.c1.is_in(["123000", "789000"]),
        {
            1: True,
            2: False,
            3: True,
            4: None,
        },
    )


def test_is_not_in(spec_test):
    spec_test(
        table_data,
        p.c1.is_not_in(["123000", "789000"]),
        {
            1: False,
            2: True,
            3: False,
            4: None,
        },
    )


def test_is_in_codelist_csv(spec_test):
    codelist = codelist_from_csv_lines(
        [
            "code",
            "123000",
            "789000",
        ],
        column="code",
    )

    spec_test(
        table_data,
        p.c1.is_in(codelist),
        {
            1: True,
            2: False,
            3: True,
            4: None,
        },
    )
