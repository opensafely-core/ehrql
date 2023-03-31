from ..tables import p


title = "Testing whether one string contains another string"


def test_contains_fixed_value(spec_test):
    table_data = {
        p: """
              |   s1
            --+--------
            1 | ab
            2 | ab12
            3 | 12ab
            4 | 12ab45
            5 | a b
            6 | AB
            7 |
            """,
    }
    spec_test(
        table_data,
        p.s1.contains("ab"),
        {
            1: True,
            2: True,
            3: True,
            4: True,
            5: False,
            6: False,
            7: None,
        },
    )


def test_contains_fixed_value_with_special_characters(spec_test):
    table_data = {
        p: """
              |  s1
            --+-------
            1 | /a%b_
            2 | /ab_
            3 | /a%bc
            4 | a%b_
            """,
    }
    spec_test(
        table_data,
        p.s1.contains("/a%b_"),
        {
            1: True,
            2: False,
            3: False,
            4: False,
        },
    )


def test_contains_value_from_column(spec_test):
    table_data = {
        p: """
              |   s1   | s2
            --+--------+----
            1 | ab     | ab
            2 | cd12   | cd
            3 | 12ef   | ef
            4 | 12gh45 | gh
            5 | i j    | ij
            6 | KL     | kl
            7 |        | mn
            8 | ab     |
            """,
    }
    spec_test(
        table_data,
        p.s1.contains(p.s2),
        {
            1: True,
            2: True,
            3: True,
            4: True,
            5: False,
            6: False,
            7: None,
            8: None,
        },
    )


def test_contains_value_from_column_with_special_characters(spec_test):
    table_data = {
        p: """
              |  s1   |  s2
            --+-------+-------
            1 | /a%b_ | /a%b_
            2 | /ab_  | /a%b_
            3 | /a%bc | /a%b_
            4 | a%b_  | /a%b_

            """,
    }
    spec_test(
        table_data,
        p.s1.contains(p.s2),
        {
            1: True,
            2: False,
            3: False,
            4: False,
        },
    )
