from ehrql import days

from ..tables import e


title = "Aggregations which apply to all series containing dates"


def test_count_episodes(spec_test):
    table_data = {
        e: """
              |     d1
            --+------------
            1 | 2020-01-01
            1 | 2020-01-04
            1 | 2020-01-06
            1 | 2020-01-10
            1 | 2020-01-12
            2 | 2020-01-01
            3 |
            4 | 2020-01-10
            4 |
            4 |
            4 | 2020-01-01
            """,
    }

    spec_test(
        table_data,
        e.d1.count_episodes_for_patient(days(3)),
        {
            1: 2,
            2: 1,
            3: 0,
            4: 2,
        },
    )
