import datetime

import sqlalchemy


def test_date_literals_have_correct_type(mssql_engine):
    case_statement = sqlalchemy.case(
        (
            sqlalchemy.literal(1) == 1,
            datetime.date(2000, 10, 5),
        ),
    )
    query = sqlalchemy.select(case_statement.label("output"))
    with mssql_engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))
    assert results[0].output == datetime.date(2000, 10, 5)
