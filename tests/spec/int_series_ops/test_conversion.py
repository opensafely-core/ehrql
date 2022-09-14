from ..tables import p

title = "Convert an integer value"

table_data = {
    p: """
          | i1 | f1
        --+----+----
        1 | 1  | 1.0
        2 | 32 | 12.4
        3 | 5  | -3.2
        4 |    | 2.1
        """,
}


def test_integer_as_float(spec_test):
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


def test_add_int_to_float(spec_test):
    spec_test(
        table_data,
        p.i1 + p.f1.as_int(),
        {1: 2, 2: 44, 3: 2, 4: None},
    )
