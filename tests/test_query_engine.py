import pytest
import sqlalchemy
from sql_setup import Base, Events, RegistrationHistory
from sqlalchemy.orm import sessionmaker

from cohortextractor.backends.base import BaseBackend, Column, SQLTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine
from cohortextractor.query_language import table
from cohortextractor.query_utils import get_column_definitions


@pytest.fixture
def db_engine_and_session():
    def create_engine_and_setup_session(db_url, drivername="mssql+pymssql"):
        url = sqlalchemy.engine.make_url(db_url)
        url = url.set(drivername=drivername)
        engine = sqlalchemy.create_engine(url, echo=True, future=True)

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        return engine, Session()

    return create_engine_and_setup_session


class MockBackend(BaseBackend):
    practice_registrations = SQLTable(
        source="practice_registrations",
        columns=dict(id=Column("id", source="PatientId")),
    )
    clinical_events = SQLTable(
        source="events", columns=dict(code=Column("code", source="EventCode"))
    )


def test_backend_tables():
    """Test that a backend registers its table names"""
    assert MockBackend.tables == {"practice_registrations", "clinical_events"}


def test_mssql_query_engine():
    """Test the simplest Cohort definition that just selects a single column"""

    class Cohort:
        output_value = table("clinical_events").get("code")

    column_definitions = get_column_definitions(Cohort)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=MockBackend(database_url=None)
    )

    sql = query_engine.get_sql()
    assert (
        sql == "SELECT * INTO group_table_0 FROM (\n"
        "SELECT clinical_events.code, clinical_events.patient_id \n"
        "FROM (SELECT EventCode AS code, PatientId AS patient_id \n"
        "FROM events) AS clinical_events\n) t\n\n\n"
        "SELECT practice_registrations.[PatientId] AS patient_id, group_table_0.code "
        "AS output_value \nFROM practice_registrations LEFT OUTER JOIN group_table_0 "
        "ON practice_registrations.[PatientId] = group_table_0.patient_id"
    )


def test_run_generated_sql(db_engine_and_session):
    # TODO use database fixture
    db_url = "mssql://SA:Your_password123!@localhost:12345/test"
    engine, session = db_engine_and_session(db_url=db_url)
    reg = RegistrationHistory(PatientId=1, StpId="STP1")
    event1 = Events(PatientId=1, EventCode="Code1")
    event2 = Events(PatientId=2, EventCode="Code2")
    session.add_all([reg, event1, event2])
    session.commit()

    class Cohort:
        output_value = table("clinical_events").get("code")

    column_definitions = get_column_definitions(Cohort)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=MockBackend(db_url)
    )
    result = query_engine.execute_query()
    assert result == [(1, "Code1")]


def test_invalid_table():
    class Cohort:
        output_value = table("unknown").get("code")

    column_definitions = get_column_definitions(Cohort)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=MockBackend(database_url=None)
    )
    with pytest.raises(ValueError, match="Unknown table 'unknown'"):
        query_engine.get_sql()
