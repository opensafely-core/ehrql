import datetime

import sqlalchemy
import sqlalchemy.orm

from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.sqlalchemy_types import Date, Integer


def test_insert_date_as_string_or_datetime():
    class Table(sqlalchemy.orm.declarative_base()):
        __tablename__ = "t"
        pk = sqlalchemy.Column(Integer, primary_key=True)
        date = sqlalchemy.Column(Date)

    engine = SQLiteQueryEngine("sqlite://").engine

    Table.metadata.create_all(engine)
    with sqlalchemy.orm.Session(engine) as session:
        session.add(Table(date="2020-10-20"))
        session.add(Table(date=datetime.date(2021, 11, 21)))
        results = list(session.execute(sqlalchemy.select(Table.date)))

    assert results == [
        (datetime.date(2020, 10, 20),),
        (datetime.date(2021, 11, 21),),
    ]
