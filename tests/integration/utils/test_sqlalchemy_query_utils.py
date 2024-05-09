import pytest
import sqlalchemy

from ehrql.utils.sqlalchemy_query_utils import InsertMany


table = sqlalchemy.Table(
    "t",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("i", sqlalchemy.Integer()),
    sqlalchemy.Column("s", sqlalchemy.String()),
)


def test_insert_many(engine):
    if engine.name == "in_memory":
        pytest.skip("SQL tests do not apply to in-memory engine")

    rows = [
        (1, "a"),
        (2, "b"),
        (3, "c"),
    ]
    insert_many = InsertMany(
        table,
        # Test that we can handle an iterator rather than just a list
        iter(rows),
    )

    with engine.sqlalchemy_engine().connect() as connection:
        connection.execute(sqlalchemy.schema.CreateTable(table))
        try:
            connection.execute(insert_many)
            response = connection.execute(sqlalchemy.select(table))
            results = list(response)
        finally:
            # Explicitly drop the table as it persists in the Trino engine
            connection.execute(sqlalchemy.schema.DropTable(table))

    assert sorted(results) == rows
