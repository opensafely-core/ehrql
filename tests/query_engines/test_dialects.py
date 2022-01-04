import datetime

import sqlalchemy

from databuilder import sqlalchemy_types


def test_datetime_column_returns_date_if_typed_as_such(engine):
    """
    Sometimes we have a datetime column in the underlying database that we want to
    represent as just a date in the schema we present to the user. This tests that we
    get the expected results over all our database dialects.
    """
    # Create a table with a pair of datetime columns and populate it
    Base = sqlalchemy.orm.declarative_base()

    class DateValue(Base):
        __tablename__ = "datetime_test_table"
        pk = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        value_as_datetime = sqlalchemy.Column(sqlalchemy.DateTime())
        value_as_date = sqlalchemy.Column(sqlalchemy.DateTime())

    engine.setup(
        DateValue(
            pk=1,
            value_as_datetime="2021-04-15 10:11:12",
            value_as_date="2020-10-20 08:09:10",
        )
    )

    # Create a SQLAlchemy Table representing the above, but with one of the datetime
    # columns typed as a date instead
    table = sqlalchemy.Table(
        DateValue.__tablename__,
        sqlalchemy.MetaData(),
        sqlalchemy.Column("value_as_datetime", sqlalchemy_types.DateTime),
        sqlalchemy.Column("value_as_date", sqlalchemy_types.Date),
    )

    # Retrieve the values we inserted
    query = sqlalchemy.select(table.c.value_as_datetime, table.c.value_as_date)
    with engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))

    # Check that we get the expected types and values
    assert results[0] == (
        datetime.datetime(2021, 4, 15, 10, 11, 12),
        datetime.date(2020, 10, 20),
    )


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
