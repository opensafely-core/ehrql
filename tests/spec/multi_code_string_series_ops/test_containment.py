from ehrql.codes import ICD10Code

from ..tables import p


title = "Testing for containment using codes"

table_data = {
    p: """
          |   m1
        --+--------
        1 | ||E119 ,J849 ,M069 ||I801 ,I802
        2 | ||T202 ,A429 ||A429 ,A420, J170
        3 | ||M139 ,E220 ,M145, M060
        4 |
        """,
}


def test_contains_code_prefix(spec_test):
    spec_test(
        table_data,
        p.m1.contains("M06"),
        {
            1: True,
            2: False,
            3: True,
            4: None,
        },
    )


def test_contains_code(spec_test):
    spec_test(
        table_data,
        p.m1.contains(ICD10Code("M069")),
        {
            1: True,
            2: False,
            3: False,
            4: None,
        },
    )


def test_contains_any_of_codelist(spec_test):
    spec_test(
        table_data,
        p.m1.contains_any_of([ICD10Code("M069"), "A429"]),
        {
            1: True,
            2: True,
            3: False,
            4: None,
        },
    )
