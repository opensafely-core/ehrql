from ..tables import e, p

title = "Defining a population"


def test_population_with_single_table(spec_test):
    table_data = {
        p: """
              | b1 | i1
            --+----+---
            1 | F  | 10
            2 | T  | 20
            3 | F  | 30
        """,
    }

    spec_test(
        table_data,
        p.i1,
        {
            1: 10,
            3: 30,
        },
        population=~p.b1,
    )


def test_population_with_multiple_tables(spec_test):
    table_data = {
        p: """
              | i1
            --+----
            1 | 10
            2 | 20
            3 | 0
        """,
        e: """
              | i1
            --+-----
            1 | 101
            1 | 102
            3 | 301
            4 | 401
        """,
    }

    spec_test(
        table_data,
        e.exists_for_patient(),
        {
            1: True,
            2: False,
        },
        population=p.i1 > 0,
    )
