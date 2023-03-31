import datetime

from ..tables import p


title = "Types usable in comparisons involving dates"

table_data = {
    p: """
          |     d1     |     d2
        --+------------+------------
        1 | 1990-01-01 | 1980-01-01
        2 | 2000-01-01 | 1980-01-01
        3 | 2010-01-01 | 2020-01-01
        4 |            | 2020-01-01
        """,
}


def test_accepts_python_date_object(spec_test):
    spec_test(
        table_data,
        p.d1.is_before(datetime.date(2000, 1, 20)),
        {
            1: True,
            2: True,
            3: False,
            4: None,
        },
    )


def test_accepts_iso_formated_date_string(spec_test):
    spec_test(
        table_data,
        p.d1.is_before("2000-01-20"),
        {
            1: True,
            2: True,
            3: False,
            4: None,
        },
    )


def test_accepts_another_date_series(spec_test):
    spec_test(
        table_data,
        p.d1.is_before(p.d2),
        {
            1: False,
            2: False,
            3: True,
            4: None,
        },
    )
