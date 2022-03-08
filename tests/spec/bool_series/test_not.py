from ..tables import p

table_data = {
    p: """
          | b1
        --+----
        1 |  T
        2 |
        3 |  F
        """,
}


def test_not(spec_test):
    spec_test(
        table_data,
        ~p.b1,
        {
            1: False,
            2: None,
            3: True,
        },
    )
