from ..tables import p

title = "Convert an integer value"


def test_integer_as_float(spec_test):
    table_data = {
        p: """
              |   i1
            --+--------
            1 | 1
            2 | 32
            3 | 5
            4 |
            """,
    }
    spec_test(
        table_data,
        p.i1.as_float(),
        {
            1: 1.0,
            2: 32.0,
            3: 5.0,
            4: None,
        },
    )


def test_integer_as_int(spec_test):
    table_data = {
        p: """
              |   i1
            --+--------
            1 | 1
            2 | 32
            3 | 5
            4 |
            """,
    }
    spec_test(
        table_data,
        p.i1.as_int(),
        {
            1: 1,
            2: 32,
            3: 5,
            4: None,
        },
    )
