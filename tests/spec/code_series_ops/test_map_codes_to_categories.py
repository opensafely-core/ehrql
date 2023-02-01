from databuilder.codes import codelist_from_csv_lines

from ..tables import p

title = "Test mapping codes to categories using a categorised codelist"

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


def test_map_codes_to_categories(spec_test):
    codelist = codelist_from_csv_lines(
        [
            "code,my_categorisation",
            "abc,cat1",
            "ghi,cat2",
        ],
        column="code",
        system="snomedct",
    )

    spec_test(
        table_data,
        p.c1.to_category(codelist.my_categorisation),
        {
            1: "cat1",
            2: None,
            3: "cat2",
            4: None,
        },
    )
