from ..tables import e, p


title = "Testing for containment"

table_data = {
    p: """
          |  i1
        --+-----
        1 | 101
        2 | 201
        3 | 301
        4 |
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
        """,
}


def test_is_in(spec_test):
    spec_test(
        table_data,
        p.i1.is_in([101, 301]),
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
        p.i1.is_not_in([101, 301]),
        {
            1: False,
            2: True,
            3: False,
            4: None,
        },
    )


def test_is_in_series(spec_test):
    spec_test(
        table_data,
        p.i1.is_in(e.i1),
        {
            1: True,
            2: True,
            3: False,
            4: None,
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
        },
    )
