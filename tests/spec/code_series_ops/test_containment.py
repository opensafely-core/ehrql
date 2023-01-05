from databuilder.codes import Codelist, SNOMEDCTCode, codelist_from_csv_lines

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
    codelist = Codelist(
        codes={SNOMEDCTCode("abc"), SNOMEDCTCode("ghi")}, category_maps={}
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
        codelists=[codelist],
    )


def test_is_not_in(spec_test):
    codelist = Codelist(
        codes={SNOMEDCTCode("abc"), SNOMEDCTCode("ghi")}, category_maps={}
    )
    spec_test(
        table_data,
        p.c1.is_not_in(codelist),
        {
            1: False,
            2: True,
            3: False,
            4: None,
        },
        codelists=[codelist],
    )


def test_is_in_codelist_csv(spec_test):

    codelist = codelist_from_csv_lines(
        [
            "code",
            "abc",
            "ghi",
        ],
        column="code",
        system="snomedct",
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
        codelists=[codelist],
    )
