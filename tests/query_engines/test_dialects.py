import datetime

import sqlalchemy

from cohortextractor import sqlalchemy_types


def test_datetime_column_returns_date_if_typed_as_such(engine):
    # Create a table with a single datetime column and populate it
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

    # Create a SQLAlchemy Table representing the above, but with `value_as_date` typed
    # as date rather than datetime
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
