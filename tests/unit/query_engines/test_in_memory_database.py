import pytest

from ehrql.query_engines.in_memory_database import (
    EventColumn,
    EventTable,
    PatientColumn,
    PatientTable,
    Rows,
    apply_function,
    apply_function_to_rows_and_values,
    handle_null,
)


def test_patient_table_repr():
    t = PatientTable.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        2 | 201 | 211
        """
    )
    assert PatientTable.parse(repr(t)) == t


def test_event_table_repr():
    t = EventTable.parse(
        """
          |   |  i1 |  i2
        --+---+-----+-----
        1 | 0 | 101 | 111
        1 | 1 | 102 | 112
        1 | 2 | 103 | 113
        2 | 3 | 203 | 211
        2 | 4 | 202 | 212
        2 | 5 | 201 | 213
        """
    )
    assert EventTable.parse(repr(t)) == t


def test_patient_column_repr():
    c = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        """
    )
    assert PatientColumn.parse(repr(c)) == c


def test_event_column_repr():
    c = EventColumn.parse(
        """
        1 | 0 | 101
        1 | 1 | 102
        2 | 2 | 201
        """
    )
    assert EventColumn.parse(repr(c)) == c


def test_rows_repr():
    rows = Rows({0: 101, 1: 102, 2: 103})
    assert repr(rows) == "Rows({0: 101, 1: 102, 2: 103})"


def test_rows_aggregate_values():
    rows = Rows({0: 101, 1: 102, 2: 103})
    assert rows.aggregate_values(sum, default=None) == 306


def test_rows_aggregate_values_ignores_nulls():
    rows = Rows({0: 101, 1: 102, 2: None})
    assert rows.aggregate_values(sum, default=None) == 203


def test_event_column_aggregate_values():
    c = EventColumn.parse(
        """
        1 | 0 | 101
        1 | 1 | 102
        1 | 2 | 103
        2 | 3 | 201
        2 | 4 | 202
        3 | 5 | 301
        """
    )

    assert c.aggregate_values(sum, default=None) == PatientColumn.parse(
        """
        1 | 306
        2 | 403
        3 | 301
        """
    )


def test_event_column_aggregate_values_ignores_nulls():
    c = EventColumn.parse(
        """
        1 | 0 |
        2 | 1 | 201
        2 | 2 |
        """
    )

    assert c.aggregate_values(sum, default=None) == PatientColumn.parse(
        """
        1 |
        2 | 201
        """
    )


def test_patient_table_exists():
    t = PatientTable.parse(
        """
          |   i
        --+----
        1 | 101
        2 | 201
        """
    )

    expected = PatientColumn.parse(
        """
        1 | T
        2 | T
        """,
        default=False,
    )

    assert t.exists() == expected


def test_event_table_exists():
    t = EventTable.parse(
        """
          |   |   i
        --+---+----
        1 | 0 | 101
        1 | 1 | 102
        2 | 2 | 201
        """
    )

    expected = PatientColumn.parse(
        """
        1 | T
        2 | T
        """,
        default=False,
    )

    assert t.exists() == expected


def test_patient_table_count():
    t = PatientTable.parse(
        """
          |   i
        --+----
        1 | 101
        2 | 201
        """
    )

    expected = PatientColumn.parse(
        """
        1 | 1
        2 | 1
        """,
        default=0,
    )

    assert t.count() == expected


def test_event_table_count():
    t = EventTable.parse(
        """
          |   |   i
        --+---+----
        1 | 0 | 101
        1 | 1 | 102
        2 | 2 | 201
        """
    )

    expected = PatientColumn.parse(
        """
        1 | 2
        2 | 1
        """,
        default=0,
    )

    assert t.count() == expected


def test_patient_column_filter():
    c = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )

    predicate = PatientColumn.parse(
        """
        1 | T
        2 | T
        3 | F
        """,
    )

    assert c.filter(predicate) == PatientColumn.parse(
        """
        1 | 101
        2 | 201
        """
    )


def test_rows_filter():
    rows = Rows({0: 101, 1: 102, 2: 103})
    assert rows.filter(Rows({0: True, 1: True, 2: False})) == Rows({0: 101, 1: 102})


def test_event_column_filter():
    c = EventColumn.parse(
        """
        1 | 0 | 101
        1 | 1 | 102
        1 | 2 | 103
        2 | 3 | 201
        2 | 4 | 202
        3 | 5 | 301
        """
    )

    predicate = EventColumn.parse(
        """
        1 | 0 | T
        1 | 1 | T
        1 | 2 | F
        2 | 3 | T
        2 | 4 | F
        3 | 5 | F
        """
    )

    # We can't compare against EventColumn.parse(...) because patient 3 has no
    # rows and we cannot represent that in a string.
    assert c.filter(predicate) == EventColumn(
        {
            1: Rows({0: 101, 1: 102}),
            2: Rows({3: 201}),
            3: Rows({}),
        }
    )


def test_patient_table_filter():
    t = PatientTable.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        2 | 201 | 211
        3 | 301 | 311
        """
    )

    predicate = PatientColumn.parse(
        """
        1 | T
        2 | T
        3 | F
        """
    )

    assert t.filter(predicate) == PatientTable.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        2 | 201 | 211
        """
    )


def test_event_table_filter():
    t = EventTable.parse(
        """
          |   |  i1 |  i2
        --+---+-----+-----
        1 | 0 | 101 | 111
        1 | 1 | 102 | 112
        1 | 2 | 103 | 113
        2 | 3 | 203 | 211
        2 | 4 | 202 | 212
        3 | 5 | 301 | 311
        """
    )

    predicate = EventColumn.parse(
        """
        1 | 0 | T
        1 | 1 | T
        1 | 2 | F
        2 | 3 | T
        2 | 4 | F
        3 | 5 | F
        """
    )

    # We can't compare against EventColumn.parse(...) because patient 3 has no
    # rows and we cannot represent that in a string.
    t.filter(predicate)["row_id"] == EventColumn(
        {
            1: Rows({0: 0, 1: 1}),
            2: Rows({3: 3}),
            3: Rows({}),
        }
    )


def test_event_table_filter_then_aggregate():
    t = EventTable.parse(
        """
          |   |  i1 |  i2
        --+---+-----+-----
        1 | 0 | 101 | 111
        1 | 1 | 102 | 112
        1 | 2 | 103 | 113
        2 | 3 | 203 | 211
        2 | 4 | 202 | 212
        3 | 5 | 301 | 311
        """
    )

    predicate = EventColumn.parse(
        """
        1 | 0 | T
        1 | 1 | T
        1 | 2 | F
        2 | 3 | T
        2 | 4 | F
        3 | 5 | F
        """
    )

    assert t.filter(predicate).count() == PatientColumn.parse(
        """
        1 | 2
        2 | 1
        3 | 0
        """,
        default=0,
    )


def test_event_table_filter_then_pick_at_index():
    t = EventTable.parse(
        """
          |   |  i1 |  i2
        --+---+-----+-----
        1 | 0 | 101 | 111
        1 | 1 | 102 | 112
        1 | 2 | 103 | 113
        2 | 3 | 203 | 211
        2 | 4 | 202 | 212
        3 | 5 | 301 | 311
        """
    )

    predicate = EventColumn.parse(
        """
        1 | 0 | T
        1 | 1 | T
        1 | 2 | F
        2 | 3 | T
        2 | 4 | F
        3 | 5 | F
        """
    )

    assert t.filter(predicate).pick_at_index(-1) == PatientTable.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 102 | 112
        2 | 203 | 211
        3 |     |
        """,
    )


def test_rows_sort_index():
    rows = Rows({0: 101, 1: 102, 2: 101})
    assert rows.sort_index() == Rows({0: 0, 1: 1, 2: 0})


def test_event_column_sort_index():
    c = EventColumn.parse(
        """
        1 | 0 | 101
        1 | 1 | 102
        1 | 2 | 103
        2 | 3 | 203
        2 | 4 | 202
        2 | 5 | 201
        """
    )

    assert c.sort_index() == EventColumn.parse(
        """
        1 | 0 | 0
        1 | 1 | 1
        1 | 2 | 2
        2 | 3 | 2
        2 | 4 | 1
        2 | 5 | 0
        """
    )


def test_rows_sort():
    rows = Rows({0: 101, 1: 102, 2: 103})
    assert rows.sort(Rows({0: 1, 1: 0, 2: 1})) == Rows({1: 102, 0: 101, 2: 103})


def test_event_column_sort():
    c = EventColumn.parse(
        """
        1 | 0 | 101
        1 | 1 | 102
        1 | 2 | 103
        2 | 3 | 203
        2 | 4 | 202
        2 | 5 | 201
        """
    )

    sort_index = c.sort_index()

    assert c.sort(sort_index) == EventColumn.parse(
        """
        1 | 0 | 101
        1 | 1 | 102
        1 | 2 | 103
        2 | 5 | 201
        2 | 4 | 202
        2 | 3 | 203
        """
    )


def test_event_table_sort():
    t = EventTable.parse(
        """
          |   |  i1 |  i2
        --+---+-----+-----
        1 | 0 | 101 | 111
        1 | 1 | 102 | 112
        1 | 2 | 103 | 113
        2 | 3 | 203 | 211
        2 | 4 | 202 | 212
        2 | 5 | 201 | 213
        """
    )

    sort_index = t["i1"].sort_index()

    assert t.sort(sort_index) == EventTable.parse(
        """
          |   |  i1 |  i2
        --+---+-----+-----
        1 | 0 | 101 | 111
        1 | 1 | 102 | 112
        1 | 2 | 103 | 113
        2 | 5 | 201 | 213
        2 | 4 | 202 | 212
        2 | 3 | 203 | 211
        """
    )


def test_rows_pick_at_index():
    rows = Rows({0: 101, 1: 102, 2: 103})
    assert rows.pick_at_index(0) == 101
    assert rows.pick_at_index(-1) == 103


def test_event_column_pick_at_index():
    c = EventColumn.parse(
        """
        1 | 0 | 101
        1 | 1 | 102
        1 | 2 | 103
        2 | 3 | 201
        2 | 4 | 202
        3 | 5 | 301
        """
    )

    assert c.pick_at_index(0) == PatientColumn.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )

    assert c.pick_at_index(-1) == PatientColumn.parse(
        """
        1 | 103
        2 | 202
        3 | 301
        """
    )


def test_event_table_pick_at_index():
    t = EventTable.parse(
        """
          |   |  i1 |  i2
        --+---+-----+-----
        1 | 0 | 101 | 113
        1 | 1 | 102 | 112
        1 | 2 | 103 | 111
        2 | 3 | 201 | 212
        2 | 4 | 202 | 211
        3 | 5 | 301 | 311
        """
    )

    assert t.pick_at_index(0) == PatientTable.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 113
        2 | 201 | 212
        3 | 301 | 311
        """
    )

    assert t.pick_at_index(-1) == PatientTable.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 103 | 111
        2 | 202 | 211
        3 | 301 | 311
        """
    )


def test_apply_function_with_event_columns():
    pc1 = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )
    pc2 = PatientColumn.parse(
        """
        1 | 102
        2 | 202
        4 | 402
        """
    )
    ec1 = EventColumn.parse(
        """
        1 | 0 | 111
        1 | 1 | 112
        2 | 2 | 211
        2 | 3 | 212
        5 | 4 | 511
        """
    )
    ec2 = EventColumn.parse(
        """
        1 | 0 | 121
        1 | 1 | 122
        2 | 2 | 221
        2 | 3 | 222
        5 | 4 | 521
        """
    )
    op = handle_null(sum_)
    results = apply_function(op, pc1, pc2, ec1, ec2)
    assert results == EventColumn.parse(
        """
        1 | 0 | 435
        1 | 1 | 437
        2 | 2 | 835
        2 | 3 | 837
        3 |   | ---
        4 |   | ---
        5 | 4 |
        """
    )


def test_apply_function_to_rows_and_values():
    args = [Rows({1: 101, 2: 201}), 1000, Rows({1: 102, 2: 202})]
    assert apply_function_to_rows_and_values(sum_, args) == Rows(
        {1: (101 + 1000 + 102), 2: (201 + 1000 + 202)}
    )


@pytest.mark.parametrize(
    "func_to_apply,extra_args",
    [
        (sum, [1000, -200]),
        (min, [200]),
        (max, [200, 300]),
    ],
)
def test_apply_function_to_rows_and_values_with_different_key_order(
    func_to_apply, extra_args
):
    def func(*args):
        return func_to_apply(args)

    same_order_args = [Rows({1: 101, 2: 201}), Rows({1: 102, 2: 202}), *extra_args]
    diff_order_args = [Rows({1: 101, 2: 201}), Rows({2: 202, 1: 102}), *extra_args]
    assert apply_function_to_rows_and_values(
        func, same_order_args
    ) == apply_function_to_rows_and_values(func, diff_order_args)


def test_apply_function_with_no_event_columns():
    pc1 = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )
    pc2 = PatientColumn.parse(
        """
        1 | 102
        2 | 202
        4 | 402
        """
    )
    op = handle_null(sum_)
    results = apply_function(op, pc1, pc2)
    assert results == PatientColumn.parse(
        """
        1 | 203
        2 | 403
        3 |
        4 |
        """
    )


def sum_(*args):
    return sum(args)
