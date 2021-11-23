import datetime

import sqlalchemy

from cohortextractor import sqlalchemy_types


def test_datetime_column_returns_date_if_typed_as_such(engine):
    # Create a table with a single datetime column and populate it
    Base = sqlalchemy.orm.declarative_base()

    class DateValue(Base):
        __tablename__ = "datetime_test_table"
        pk = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        value = sqlalchemy.Column(sqlalchemy.DateTime())

    engine.setup(DateValue(pk=1, value="2020-10-20 08:09:10"))

    # Create a SQLAlchemy Table representing the above, but with `value` typed as date
    # rather than datetime
    table = sqlalchemy.Table(
        DateValue.__tablename__,
        sqlalchemy.MetaData(),
        sqlalchemy.Column("value", sqlalchemy_types.Date),
    )

    # Retrieve the value we inserted
    with engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(sqlalchemy.select(table.c.value)))

    # Check that it's a date, not a datetime
    assert results[0][0] == datetime.date(2020, 10, 20)
