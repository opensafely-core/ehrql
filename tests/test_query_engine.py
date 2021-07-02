import pytest
import sqlalchemy
from sql_setup import Base, Events, RegistrationHistory
from sqlalchemy.orm import sessionmaker

from cohortextractor.backends.mock import MockBackend
from cohortextractor.main import extract
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
        "FROM (SELECT EventCode AS code, Date AS date, PatientId AS patient_id \n"
        "FROM events) AS clinical_events\n) t\n\n\n"
        "SELECT practice_registrations.[PatientId] AS patient_id, group_table_0.code "
        "AS output_value \nFROM practice_registrations LEFT OUTER JOIN group_table_0 "
        "ON practice_registrations.[PatientId] = group_table_0.patient_id"
    )


def set_up_test_data(database, load_data, db_engine_and_session):
    # Load data with a dummy SQL command; this will just set up the database
    load_data(sql="GO")
    # Create the sqlalchemy engine and set up the session for the test data
    engine, session = db_engine_and_session(db_url=database.host_url())
    # Load test data
    reg = RegistrationHistory(PatientId=1, StpId="STP1")
    event1 = Events(PatientId=1, EventCode="Code1")
    event2 = Events(PatientId=2, EventCode="Code2")
    session.add_all([reg, event1, event2])
    session.commit()


@pytest.mark.integration
def test_run_generated_sql_get_single_column(
    database, load_data, db_engine_and_session
):
    set_up_test_data(database, load_data, db_engine_and_session)

    # Cohort to extract all clinical events and return just the code column
    # Note that the RegistrationHistory table is used for the default population query
    # It will join the two tables on patient_id and only rows that exist in the RegistrationHistory
    # table will be returned
    class Cohort:
        output_value = table("clinical_events").get("code")

    column_definitions = get_column_definitions(Cohort)

    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=MockBackend(database.host_url())
    )
    with query_engine.execute_query() as result:
        assert list(result) == [(1, "Code1")]


@pytest.mark.integration
def test_extract_get_single_column(database, load_data, db_engine_and_session):
    set_up_test_data(database, load_data, db_engine_and_session)

    # Cohort to extract all clinical events and return just the code column
    # Note that the RegistrationHistory table is used for the default population query
    # It will join the two tables on patient_id and only rows that exist in the RegistrationHistory
    # table will be returned
    class Cohort:
        output_value = table("clinical_events").get("code")

    backend = MockBackend(database.host_url())
    result = extract(Cohort, backend)
    assert list(result) == [{"patient_id": 1, "output_value": "Code1"}]


def test_invalid_table():
    class Cohort:
        output_value = table("unknown").get("code")

    column_definitions = get_column_definitions(Cohort)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=MockBackend(database_url=None)
    )
    with pytest.raises(ValueError, match="Unknown table 'unknown'"):
        query_engine.get_sql()
