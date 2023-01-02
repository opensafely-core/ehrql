import pytest
import sqlalchemy


def test_case_statement(engine):
    """
    Test a basic CASE statement returning a string value. This exposed a bug in the
    string handling of our Spark dialect so it's useful to keep it around.
    """
    if engine.name == "in_memory":
        pytest.skip("SQLAlchemy dialect tests do not apply to the in-memory engine")

    case_statement = sqlalchemy.case(
        (sqlalchemy.literal(1) == 0, "foo"),
        (sqlalchemy.literal(1) == 1, "bar"),
    )
    query = sqlalchemy.select(case_statement.label("output"))
    with engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))
    assert results[0].output == "bar"
