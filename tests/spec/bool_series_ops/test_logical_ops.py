import pytest

from ..tables import p

title = "Logical operations"


@pytest.mark.sql_spec
def test_not(spec_test):
    table_data = {
        p: """
              | b1
            --+----
            1 |  T
            2 |
            3 |  F
            """,
    }

    spec_test(
        table_data,
        ~p.b1,
        {
            1: False,
            2: None,
            3: True,
        },
    )


table_data = {
    p: """
          | b1 | b2
        --+----+----
        1 |  T |  T
        2 |  T |
        3 |  T |  F
        4 |    |  T
        5 |    |
        6 |    |  F
        7 |  F |  T
        8 |  F |
        9 |  F |  F
        """,
}


@pytest.mark.sql_spec
def test_and(spec_test):
    spec_test(
        table_data,
        p.b1 & p.b2,
        {
            1: True,
            2: None,
            3: False,
            4: None,
            5: None,
            6: False,
            7: False,
            8: False,
            9: False,
        },
    )


@pytest.mark.sql_spec
def test_or(spec_test):
    spec_test(
        table_data,
        p.b1 | p.b2,
        {
            1: True,
            2: True,
            3: True,
            4: True,
            5: None,
            6: None,
            7: True,
            8: None,
            9: False,
        },
    )
