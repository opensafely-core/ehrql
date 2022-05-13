from ..tables import p

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
