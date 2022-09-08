from databuilder.ehrql import case, when

from ..tables import e, p

title = "Defining a population"
text = """
`set_population` is used to limit the population from which data is extracted.
"""


def test_population_with_single_table(spec_test):
    """
    Extract a column from a patient table after limiting the population by another column.
    """
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
    """
    Limit the patient population by a column in one table, and return values from another
    table.
    """
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


def test_case_with_case_expression(spec_test):
    """
    Limit the patient population by a case expression.
    """
    table_data = {
        p: """
              | i1
            --+---
            1 | 6
            2 | 7
            3 | 9
            4 |
            """,
    }

    spec_test(
        table_data,
        p.i1,
        {
            1: 6,
            2: 7,
        },
        population=case(
            when(p.i1 <= 8).then(True),
            when(p.i1 > 8).then(False),
        ),
    )
