from ehrql import when

from ..tables import e, p


title = "Pointless sort operations that we should nevertheless handle without error"

table_data = {
    e: """
          |  i1
        --+----
        1 | 101
        2 | 201
        """,
    p: """
          |  i1
        --+----
        1 | 10
        2 | 20
        """,
}


def test_sort_by_patient_series(spec_test):
    spec_test(
        table_data,
        e.sort_by(
            # Patient series
            p.i1,
            # Literal constant
            0,
            # Compound expression which evaluates to a constant
            when(True).then(1).otherwise(0),
        )
        .first_for_patient()
        .i1,
        {
            1: 101,
            2: 201,
        },
    )
