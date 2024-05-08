from ehrql.query_model.nodes import Column, TableSchema

from .conftest import parse_row, parse_table


def test_parse_table():
    assert parse_table(
        TableSchema(i1=Column(int), i2=Column(int)),
        """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        2 | 201 |
        """,
    ) == [
        {"patient_id": 1, "i1": 101, "i2": 111},
        {"patient_id": 2, "i1": 201, "i2": None},
    ]


def test_parse_row():
    assert parse_row(
        {"patient_id": int, "i1": int, "i2": int},
        ["patient_id", "i1", "i2"],
        "1 | 101 | 111",
    ) == {"patient_id": 1, "i1": 101, "i2": 111}
