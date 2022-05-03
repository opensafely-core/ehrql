from operator import add, neg

from .database import Column, Table


def test_table_repr():
    t = Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        1 | 102 | 112
        1 | 103 | 113
        2 | 203 | 211
        2 | 202 | 212
        2 | 201 | 213
        """
    )
    assert Table.parse(repr(t)) == t


def test_column_repr():
    c = Column.parse(
        """
        1 | 101
        1 | 102
        2 | 201
        """
    )
    assert Column.parse(repr(c)) == c


def test_column_unary_op():
    c = Column.parse(
        """
        1 | 101
        1 | 102
        2 | 201
        """,
        default=0,
    )
    assert c.unary_op(neg) == Column.parse(
        """
        1 | -101
        1 | -102
        2 | -201
        """,
        default=0,
    )


def test_column_unary_op_with_null():
    c = Column.parse(
        """
        1 | 101
        1 |
        2 | 201
        """
    )
    assert c.unary_op_with_null(neg) == Column.parse(
        """
        1 | -101
        1 |
        2 | -201
        """
    )


def test_patient_column_binary_op_patient_column():
    pc1 = Column.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )
    pc2 = Column.parse(
        """
        1 | 111
        2 | 211
        4 | 411
        """
    )
    assert pc1.binary_op_with_null(add, pc2) == Column.parse(
        """
        1 | 212
        2 | 412
        3 |
        4 |
        """
    )


def test_patient_column_binary_op_event_column():
    pc = Column.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )
    ec = Column.parse(
        """
        1 | 111
        1 | 112
        2 | 211
        2 | 212
        4 | 414
        """
    )
    assert pc.binary_op_with_null(add, ec) == Column.parse(
        """
        1 | 212
        1 | 213
        2 | 412
        2 | 413
        3 |
        4 |
        """
    )


def test_event_column_binary_op_patient_column():
    pc = Column.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )
    ec = Column.parse(
        """
        1 | 111
        1 | 112
        2 | 211
        2 | 212
        4 | 411
        """
    )
    assert ec.binary_op_with_null(add, pc) == Column.parse(
        """
        1 | 212
        1 | 213
        2 | 412
        2 | 413
        3 |
        4 |
        """
    )


def test_event_column_binary_op_event_column():
    es1 = Column.parse(
        """
        1 | 101
        1 | 102
        2 | 201
        2 | 202
        3 | 301
        """
    )
    es2 = Column.parse(
        """
        1 | 111
        1 | 112
        2 | 211
        2 | 212
        3 | 311
        """
    )

    assert es1.binary_op_with_null(add, es2) == Column.parse(
        """
        1 | 212
        1 | 214
        2 | 412
        2 | 414
        3 | 612
        """
    )


def test_column_aggregate_values():
    c = Column.parse(
        """
        1 | 101
        1 | 102
        1 | 103
        2 | 201
        2 | 202
        3 | 301
        """
    )

    assert c.aggregate_values(len, default=None) == Column.parse(
        """
        1 | 3
        2 | 2
        3 | 1
        """
    )


def test_table_exists():
    t = Table.parse(
        """
          |   i
        --+----
        1 | 101
        1 | 102
        2 | 201
        """
    )

    expected = Column.parse(
        """
        1 | 1
        2 | 1
        """
    )
    expected.default = False

    # This relies on equality of 1 and True
    assert t.exists() == expected


def test_table_count():
    t = Table.parse(
        """
          |   i
        --+----
        1 | 101
        1 | 102
        2 | 201
        """
    )

    expected = Column.parse(
        """
        1 | 2
        2 | 1
        """
    )
    expected.default = 0

    assert t.count() == expected


def test_column_filter():
    c = Column.parse(
        """
        1 | 101
        1 | 102
        1 | 103
        2 | 201
        2 | 202
        3 | 301
        """
    )

    predicate = Column(
        {
            1: [True, True, False],
            2: [True, False],
            3: [False],
        },
        default=None,
    )

    assert c.filter(predicate) == Column.parse(
        """
        1 | 101
        1 | 102
        2 | 201
        """
    )


def test_table_filter():
    t = Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        1 | 102 | 112
        1 | 103 | 113
        2 | 203 | 211
        2 | 202 | 212
        3 | 301 | 311
        """
    )

    predicate = Column(
        {
            1: [True, True, False],
            2: [True, False],
            3: [False],
        },
        default=None,
    )

    assert t.filter(predicate) == Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        1 | 102 | 112
        2 | 203 | 211
        """
    )


def test_column_sort_index():
    c = Column.parse(
        """
        1 | 101
        1 | 102
        1 | 103
        2 | 203
        2 | 202
        2 | 201
        """
    )

    assert c.sort_index() == Column.parse(
        """
        1 | 0
        1 | 1
        1 | 2
        2 | 2
        2 | 1
        2 | 0
        """
    )


def test_column_sort():
    c = Column.parse(
        """
        1 | 101
        1 | 102
        1 | 103
        2 | 203
        2 | 202
        2 | 201
        """
    )

    sort_index = c.sort_index()

    assert c.sort(sort_index) == Column.parse(
        """
        1 | 101
        1 | 102
        1 | 103
        2 | 201
        2 | 202
        2 | 203
        """
    )


def test_table_sort():
    t = Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        1 | 102 | 112
        1 | 103 | 113
        2 | 203 | 211
        2 | 202 | 212
        2 | 201 | 213
        """
    )

    sort_index = t["i1"].sort_index()

    assert t.sort(sort_index) == Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        1 | 102 | 112
        1 | 103 | 113
        2 | 201 | 213
        2 | 202 | 212
        2 | 203 | 211
        """
    )


def test_column_pick_at_index():
    c = Column.parse(
        """
        1 | 101
        1 | 102
        1 | 103
        2 | 201
        2 | 202
        3 | 301
        """
    )

    assert c.pick_at_index(0) == Column.parse(
        """
        1 | 101
        2 | 201
        3 | 301
        """
    )

    assert c.pick_at_index(-1) == Column.parse(
        """
        1 | 103
        2 | 202
        3 | 301
        """
    )


def test_table_pick_at_index():
    t = Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 113
        1 | 102 | 112
        1 | 103 | 111
        2 | 201 | 212
        2 | 202 | 211
        3 | 301 | 311
        """
    )

    assert t.pick_at_index(0) == Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 113
        2 | 201 | 212
        3 | 301 | 311
        """
    )

    assert t.pick_at_index(-1) == Table.parse(
        """
          |  i1 |  i2
        --+-----+-----
        1 | 103 | 111
        2 | 202 | 211
        3 | 301 | 311
        """
    )
