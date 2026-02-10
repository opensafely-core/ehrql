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
        query_engine_class = engine.query_engine_class

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


@pytest.mark.parametrize("materialize", [True, False])
def test_query_table(engine, materialize):
    if engine.name == "in_memory":
        pytest.skip("doesn't apply to non-SQL engines")

    class TestBackend(SQLBackend):
        query_engine_class = engine.query_engine_class

        # Define a table which is a VIEW-like representation of data from multiple
        # underlying tables
        events = QueryTable(
            """
            /* test query */
            SELECT * FROM event_source_1
            UNION ALL
            SELECT * FROM event_source_2
            """,
            materialize=materialize,
        )

    engine.setup(
        EventSource1(patient_id=1, date=datetime.date(2000, 1, 1)),
        EventSource2(patient_id=1, date=datetime.date(1999, 1, 1)),
        EventSource2(patient_id=2, date=datetime.date(2002, 1, 1)),
    )

    dataset = create_dataset()
    dataset.define_population(events.exists_for_patient())
    dataset.min_date = events.date.minimum_for_patient()
    dataset.max_date = events.date.maximum_for_patient()

    engine_kwargs = {"backend": TestBackend()}
    results = engine.extract(dataset, **engine_kwargs)
    queries = engine.dump_dataset_sql(dataset, **engine_kwargs)

    assert results == [
        {
            "patient_id": 1,
            "min_date": datetime.date(1999, 1, 1),
            "max_date": datetime.date(2000, 1, 1),
        },
        {
            "patient_id": 2,
            "min_date": datetime.date(2002, 1, 1),
            "max_date": datetime.date(2002, 1, 1),
        },
    ]

    # Check how many times we see the test query in the SQL
    test_query_count = "\n".join(queries).count("/* test query */")
    if materialize:
        # If the QueryTable is materialized we should only see it executed once
        assert test_query_count == 1
    else:
        # Otherwise we expect it to be executed multiple times
        assert test_query_count > 1


def test_query_table_from_function(engine):
    if engine.name == "in_memory":
        pytest.skip("doesn't apply to non-SQL engines")

    class TestBackend(SQLBackend):
        query_engine_class = engine.query_engine_class

        # Define a table which is a VIEW-like representation of data from multiple
        # underlying tables and is dynamically generated based on the state of the
        # backend
        @QueryTable.from_function
        def events(self):
            return f"""
            /* {self.environ["value"]} */
            SELECT * FROM event_source_1
            UNION ALL
            SELECT * FROM event_source_2
            """

    engine.setup(
        EventSource1(patient_id=1, date=datetime.date(2000, 1, 1)),
        EventSource2(patient_id=2, date=datetime.date(2002, 1, 1)),
    )

    dataset = create_dataset()
    dataset.define_population(events.exists_for_patient())
    dataset.max_date = events.date.maximum_for_patient()

    magic_word = "foobar"
    engine_kwargs = {"backend": TestBackend(environ={"value": magic_word})}
    results = engine.extract(dataset, **engine_kwargs)
    queries = engine.dump_dataset_sql(dataset, **engine_kwargs)

    assert results == [
        {
            "patient_id": 1,
            "max_date": datetime.date(2000, 1, 1),
        },
        {
            "patient_id": 2,
            "max_date": datetime.date(2002, 1, 1),
        },
    ]

    # Confirm that our dynamically generated value made it in to the SQL
    sql_text = "\n".join(queries)
    assert magic_word in sql_text
