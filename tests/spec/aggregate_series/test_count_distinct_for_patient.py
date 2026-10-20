from ..tables import e


title = "Count distinct aggregation"

table_data = {
    e: r"""
          |  i1 |  f1 | s1 |     d1     |  by1
        --+-----+-----+----+------------+-------
        1 | 101 | 1.1 |  a | 2020-01-01 | \xa1\x01
        1 | 102 | 1.2 |  b | 2020-01-02 | \xa1\x02
        1 | 103 | 1.5 |  c | 2020-01-03 | \xa1\x03
        2 | 201 | 2.1 |  a | 2020-02-01 | \xb2\x01
        2 | 201 | 2.1 |  a | 2020-02-01 | \xb2\x01
        2 | 203 | 2.5 |  b | 2020-02-02 | \xb2\x03
        3 | 301 | 3.1 |  a | 2020-03-01 | \xc3\x01
        3 | 301 | 3.1 |  a | 2020-03-01 | \xc3\x01
        3 |     |     |    |            |
        3 |     |     |    |            |
        4 |     |     |    |            |
        """,
}


def test_count_distinct_for_patient_integer(spec_test):
    spec_test(
        table_data,
        e.i1.count_distinct_for_patient(),
        {
            1: 3,
            2: 2,
            3: 1,
            4: 0,
        },
    )


def test_count_distinct_for_patient_float(spec_test):
    spec_test(
        table_data,
        e.f1.count_distinct_for_patient(),
        {
            1: 3,
            2: 2,
            3: 1,
            4: 0,
        },
    )


def test_count_distinct_for_patient_string(spec_test):
    spec_test(
        table_data,
        e.s1.count_distinct_for_patient(),
        {
            1: 3,
            2: 2,
            3: 1,
            4: 0,
        },
    )


def test_count_distinct_for_patient_date(spec_test):
    spec_test(
        table_data,
        e.d1.count_distinct_for_patient(),
        {
            1: 3,
            2: 2,
            3: 1,
            4: 0,
        },
    )


def test_count_distinct_for_patient_bytes(spec_test):
    spec_test(
        table_data,
        e.by1.count_distinct_for_patient(),
        {
            1: 3,
            2: 2,
            3: 1,
            4: 0,
        },
    )
