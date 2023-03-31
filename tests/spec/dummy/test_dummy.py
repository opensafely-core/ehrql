from ..tables import p


title = "Dummy section for testing spec generation"
text = "This section should not appear in the table of contents"


table_data = {
    p: """
          | b1 | b2
        --+----+----
        1 |  T |  T
        2 |  T |
        3 |  T |  F
        4 |    |  T
        5 |    |
        6 |    |  F
        7 |  F |  T
        8 |  F |
        9 |  F |  F
        """,
}


def test_function_with_docstring(spec_test):
    """this docstring should appear in the spec"""
    spec_test(
        table_data,
        p.b1 & p.b2,
        {
            1: True,
            2: None,
            3: False,
            4: None,
            5: None,
            6: False,
            7: False,
            8: False,
            9: False,
        },
    )


def test_function_without_docstring(spec_test):
    spec_test(
        table_data,
        p.b1 & p.b2,
        {
            1: True,
            2: None,
            3: False,
            4: None,
            5: None,
            6: False,
            7: False,
            8: False,
            9: False,
        },
    )
