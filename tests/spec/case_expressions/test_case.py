from databuilder.ehrql import case, when

from ..tables import p

title = "Logical case expressions"

table_data = {
    p: """
          | i1
        --+----
        1 | 6
        2 | 7
        3 | 8
        4 | 9
        5 |
        """,
}


def test_case_with_expression(spec_test):
    spec_test(
        table_data,
        case(
            when(p.i1 < 8).then(p.i1),
            when(p.i1 > 8).then(100),
        ),
        {
            1: 6,
            2: 7,
            3: None,
            4: 100,
            5: None,
        },
    )


def test_case_with_default(spec_test):
    spec_test(
        table_data,
        case(
            when(p.i1 < 8).then(p.i1),
            when(p.i1 > 8).then(100),
            default=0,
        ),
        {
            1: 6,
            2: 7,
            3: 0,
            4: 100,
            5: 0,
        },
    )


def test_case_with_boolean_column(spec_test):
    table_data = {
        p: """
              | i1 | b1
            --+----+----
            1 | 6  | T
            2 | 7  | F
            3 | 9  | F
            4 |
            """,
    }

    spec_test(
        table_data,
        case(
            when(p.b1).then(p.i1),
            when(p.i1 > 8).then(100),
        ),
        {
            1: 6,
            2: None,
            3: 100,
            4: None,
        },
    )
