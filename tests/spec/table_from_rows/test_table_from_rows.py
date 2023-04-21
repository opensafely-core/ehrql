from ehrql.tables import PatientFrame, Series, table_from_rows

from ..tables import p


title = "Defining a table using inline data"

table_data = {
    p: """
          | i1
        --+----
        1 | 10
        2 | 20
        3 | 30
        """,
}


def test_table_from_rows(spec_test):
    inline_data = [
        (1, 100),
        (3, 300),
    ]

    @table_from_rows(inline_data)
    class t(PatientFrame):
        n = Series(int)

    spec_test(
        table_data,
        p.i1 + t.n,
        {
            1: 10 + 100,
            2: None,
            3: 30 + 300,
        },
    )
