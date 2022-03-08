from .conftest import parse_row, parse_table


def test_parse_table():
    assert (
        parse_table(
            """
          |  i1 |  i2
        --+-----+-----
        1 | 101 | 111
        2 | 201 |
        """,
        )
        == [
            {"PatientId": 1, "i1": 101, "i2": 111},
            {"PatientId": 2, "i1": 201, "i2": None},
        ]
    )


def test_parse_row():
    assert parse_row(
        ["PatientId", "i1", "i2"],
        "1 | 101 | 111",
    ) == {"PatientId": 1, "i1": 101, "i2": 111}
