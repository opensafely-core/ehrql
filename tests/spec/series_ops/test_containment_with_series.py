from ..tables import e, p


title = "Testing for containment in another series"


table_data = {
    p: """
          |  i1
        --+-----
        1 | 101
        2 | 201
        3 | 301
        4 |
        5 | 501
        6 |
        """,
    e: """
          |  i1
        --+-----
        1 | 101
        2 | 201
        2 | 203
        2 | 301
        3 | 333
        3 | 334
        4 |
        4 | 401
        5 |
        5 | 101
        """,
}


def test_is_in_series(spec_test):
    spec_test(
        table_data,
        p.i1.is_in(e.i1),
        {
            1: True,
            2: True,
            3: False,
            4: None,
            5: False,
            6: False,
        },
    )


def test_is_not_in_series(spec_test):
    spec_test(
        table_data,
        p.i1.is_not_in(e.i1),
        {
            1: False,
            2: False,
            3: True,
            4: None,
            5: True,
            6: True,
        },
    )
