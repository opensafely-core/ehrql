from ..tables import e


title = "Mixing the order of `sort_by` and `where` operations"

table_data = {
    e: """
          |  i1 | i2
        --+-----+---
        1 | 101 | 1
        1 | 102 | 2
        1 | 103 | 2
        2 | 203 | 1
        2 | 202 | 2
        2 | 201 | 2
        """,
}


def test_sort_by_before_where(spec_test):
    spec_test(
        table_data,
        e.sort_by(e.i1).where(e.i1 > 102).first_for_patient().i1,
        {
            1: 103,
            2: 201,
        },
    )


def test_sort_by_interleaved_with_where(spec_test):
    spec_test(
        table_data,
        e.sort_by(e.i1).where(e.i2 > 1).sort_by(e.i2).first_for_patient().i1,
        {
            1: 102,
            2: 201,
        },
    )
