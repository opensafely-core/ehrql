from ..tables import p

title = "Operations which apply to all series containing dates"

table_data = {
    p: """
          |     d1
        --+------------
        1 | 1990-01-02
        2 | 2000-03-04
        3 |
        """,
}


def test_get_year(spec_test):
    spec_test(
        table_data,
        p.d1.year,
        {
            1: 1990,
            2: 2000,
            3: None,
        },
    )


def test_get_month(spec_test):
    spec_test(
        table_data,
        p.d1.month,
        {
            1: 1,
            2: 3,
            3: None,
        },
    )


def test_get_day(spec_test):
    spec_test(
        table_data,
        p.d1.day,
        {
            1: 2,
            2: 4,
            3: None,
        },
    )
