from ehrql.codes import codelist_from_csv_lines

from ..tables import p


title = "Test mapping codes to categories using a categorised codelist"

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


def test_map_codes_to_categories(spec_test):
    codelist = codelist_from_csv_lines(
        [
            "code,my_categorisation",
            "123000,cat1",
            "789000,cat2",
        ],
        column="code",
        category_column="my_categorisation",
    )

    spec_test(
        table_data,
        p.c1.to_category(codelist),
        {
            1: "cat1",
            2: None,
            3: "cat2",
            4: None,
        },
    )
