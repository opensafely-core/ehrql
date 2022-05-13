from databuilder.codes import SNOMEDCTCode

from ..tables import p

title = "Testing for containment using codes"

table_data = {
    p: """
          |  c1
        --+-----
        1 | abc
        2 | def
        3 | ghi
        4 |
        """,
}


def test_is_in(spec_test):
    spec_test(
        table_data,
        p.c1.is_in([SNOMEDCTCode("abc"), SNOMEDCTCode("ghi")]),
        {
            1: True,
            2: False,
            3: True,
            4: None,
        },
    )
