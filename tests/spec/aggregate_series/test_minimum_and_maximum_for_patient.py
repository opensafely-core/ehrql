from ..tables import e


title = "Minimum and maximum aggregations"

table_data = {
    e: """
          |  i1
        --+-----
        1 | 101
        1 | 102
        1 | 103
        2 | 201
        2 |
        3 |
        """,
}


def test_minimum_for_patient(spec_test):
    spec_test(
        table_data,
        e.i1.minimum_for_patient(),
        {
            1: 101,
            2: 201,
            3: None,
        },
    )


def test_maximum_for_patient(spec_test):
    spec_test(
        table_data,
        e.i1.maximum_for_patient(),
        {
            1: 103,
            2: 201,
            3: None,
        },
    )
