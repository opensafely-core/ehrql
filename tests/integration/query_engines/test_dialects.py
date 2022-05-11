import sqlalchemy


def test_case_statement(engine):
    """
    Test a basic CASE statement returning a string value. This exposed a bug in the
    string handling of our Spark dialect so it's useful to keep it around.
    """
    case_statement = sqlalchemy.case(
        [
            (sqlalchemy.literal(1) == 0, "foo"),
            (sqlalchemy.literal(1) == 1, "bar"),
        ]
    )
    query = sqlalchemy.select(case_statement.label("output"))
    with engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))
    assert results[0]["output"] == "bar"
