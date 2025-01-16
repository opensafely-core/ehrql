from ..tables import p


title = "Convert a float value"

table_data = {
    p: """
         | b1
       --+----
       1 |  T
       2 |
       3 |  F
       """,
}


def test_bool_as_int(spec_test):
    """
    Booleans are converted to 0 or 1.
    """
    spec_test(
        table_data,
        p.b1.as_int(),
        {1: 1, 2: None, 3: 0},
    )
