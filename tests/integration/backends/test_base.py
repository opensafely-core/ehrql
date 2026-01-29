import datetime

import pytest
import sqlalchemy

from ehrql import create_dataset
from ehrql.backends.base import MappedTable, QueryTable, SQLBackend
from ehrql.tables import EventFrame, Series, table


Base = sqlalchemy.orm.declarative_base()


@table
class events(EventFrame):
    date = Series(datetime.date)


# The names in this table don't match the names we use above
class EventRecord(Base):
    __tablename__ = "event_record"
    pk = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    PatientId = sqlalchemy.Column(sqlalchemy.Integer)
    EventDate = sqlalchemy.Column(sqlalchemy.Date)


# The records for these events are split over two tables
class EventSource1(Base):
    __tablename__ = "event_source_1"
    patient_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date)


class EventSource2(Base):
    __tablename__ = "event_source_2"
    patient_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date)


def test_mapped_table(engine):
    if engine.name == "in_memory":
        pytest.skip("doesn't apply to non-SQL engines")

    class TestBackend(SQLBackend):
        display_name = "TestBackend"
        query_engine_class = engine.query_engine_class
        patient_join_column = "patient_id"

        # Define a table whose name and column names don't match the user-facing schema
        events = MappedTable(
            source="event_record",
            columns=dict(
                patient_id="PatientId",
                date="EventDate",
            ),
        )

    engine.setup(
        EventRecord(PatientId=1, EventDate=datetime.date(2001, 2, 3)),
    )

    dataset = create_dataset()
    dataset.define_population(events.exists_for_patient())
    dataset.max_date = events.date.maximum_for_patient()

    results = engine.extract(dataset, backend=TestBackend())
    assert results == [
        {"patient_id": 1, "max_date": datetime.date(2001, 2, 3)},
    ]


def test_query_table(engine):
    if engine.name == "in_memory":
        pytest.skip("doesn't apply to non-SQL engines")

    class TestBackend(SQLBackend):
        display_name = "TestBackend"
        query_engine_class = engine.query_engine_class
        patient_join_column = "patient_id"

        # Define a table which is a VIEW-like representation of data from multiple
        # underlying tables
        events = QueryTable(
            """
            SELECT * FROM event_source_1
            UNION ALL
            SELECT * FROM event_source_2
            """
        )

    engine.setup(
        EventSource1(patient_id=1, date=datetime.date(2000, 1, 1)),
        EventSource2(patient_id=1, date=datetime.date(1999, 1, 1)),
        EventSource2(patient_id=2, date=datetime.date(2002, 1, 1)),
    )

    dataset = create_dataset()
    dataset.define_population(events.exists_for_patient())
    dataset.max_date = events.date.maximum_for_patient()

    results = engine.extract(dataset, backend=TestBackend())
    assert results == [
        {"patient_id": 1, "max_date": datetime.date(2000, 1, 1)},
        {"patient_id": 2, "max_date": datetime.date(2002, 1, 1)},
    ]
