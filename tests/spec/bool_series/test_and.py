from ..tables import p

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


def test_and(spec_test):
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
