from databuilder.query_language import case, when

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


def test_case(spec_test):
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
