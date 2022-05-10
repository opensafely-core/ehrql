import pytest

from ..tables import e

title = "Including rows"


def test_take_with_column(spec_test):
    table_data = {
        e: """
              |  i1 |  b1
            --+-----+-----
            1 | 101 |  T
            1 | 102 |  T
            1 | 103 |
            2 | 201 |  T
            2 | 202 |
            2 | 203 |  F
            3 | 301 |
            3 | 302 |  F
        """,
    }

    spec_test(
        table_data,
        e.take(e.b1).i1.sum_for_patient(),
        {
            1: (101 + 102),
            2: 201,
            3: None,
        },
    )


def test_take_with_expr(spec_test):
    table_data = {
        e: """
              |  i1 |  i2
            --+-----+-----
            1 | 101 | 111
            1 | 102 | 112
            1 | 103 | 113
            2 | 201 | 211
            2 | 202 | 212
            2 | 203 | 213
            3 | 301 |
        """,
    }

    spec_test(
        table_data,
        e.take((e.i1 + e.i2) < 413).i1.sum_for_patient(),
        {
            1: (101 + 102 + 103),
            2: 201,
            3: None,
        },
    )


@pytest.mark.xfail_in_memory
def test_chain_multiple_takes(spec_test):
    table_data = {
        e: """
              | i1 | b1
            --+----+----
            1 | 1  | T
            1 | 2  | T
            1 | 3  | F
            """,
    }

    spec_test(
        table_data,
        e.take(e.i1 >= 2).take(e.b1).i1.sum_for_patient(),
        {
            1: 2,
        },
    )


# TODO: This isn't actually a spec test and should be moved elsewhere once we have the
# mechanics in place to run non-spec tests against multiple query engines. But I want to
# capture somewhere the currently working behaviour of the in-memory engine and this
# will do for now.
def test_multiple_takes_without_chaining(spec_test):
    table_data = {
        e: """
              | i1 | b1
            --+----+----
            1 | 1  | T
            1 | 2  | T
            1 | 3  | F
            """,
    }

    f1 = e.take(e.i1 >= 2)
    f2 = f1.take(f1.b1)

    spec_test(
        table_data,
        f2.i1.sum_for_patient(),
        {
            1: 2,
        },
    )
