import pytest
import sqlalchemy
from sql_setup import Base, Events, PositiveTests, RegistrationHistory
from sqlalchemy.orm import sessionmaker

from cohortextractor.backends import MockBackend
from cohortextractor.backends.base import BaseBackend, Column, SQLTable
from cohortextractor.main import extract
from cohortextractor.query_engines.mssql import MssqlQueryEngine
from cohortextractor.query_language import table
from cohortextractor.query_utils import get_column_definitions
from tests.conftest import is_fast_mode


DEFAULT_TABLES = {
    "practice_registrations": SQLTable(
        source="practice_registrations",
        columns=dict(patient_id=Column("int", source="PatientId")),
    ),
    "clinical_events": SQLTable(
        source="events",
        columns=dict(
            code=Column("varchar", source="EventCode"),
            date=Column("varchar", source="Date"),
        ),
    ),
}


@pytest.fixture
def mock_backend():
    class MockTestBackend(BaseBackend):
        """
        A backend class which has no class-defined tables and sets up its tables
        on init
        """

        backend_id = "testing"
        query_engine_class = MssqlQueryEngine

        def __init__(self, database_url, **tables):
            super(MockTestBackend, self).__init__(database_url)
            for table_name, sql_table in tables.items():
                setattr(self, table_name, sql_table)
            self.tables = tables.keys()

    def create_backend(database_url, tables=None):
        if tables is None:
            tables = DEFAULT_TABLES
        return MockTestBackend(database_url, **tables)

    return create_backend


@pytest.fixture
def setup_test_database(database, load_data):
    db_url = database.host_url()

    def setup(input_data, drivername="mssql+pymssql"):
        if not is_fast_mode():
            # call Load data with a dummy SQL command; this will just ensure the container
            # is started, with the test database created
            load_data(sql="GO")

        # Create engine
        url = sqlalchemy.engine.make_url(db_url)
        url = url.set(drivername=drivername)
        engine = sqlalchemy.create_engine(url, echo=True, future=True)
        # Reset the schema
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        # Create session
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        # Load test data
        session.add_all(input_data)
        session.commit()

    return setup


def test_backend_tables():
    """Test that a backend registers its table names"""
    # Use the base MockBackend for this test, so we're testing the real __init_subclass__ method
    assert MockBackend.tables == {"practice_registrations", "clinical_events"}


def test_mssql_query_engine(mock_backend):
    """Test the simplest Cohort definition that just selects a single column"""

    class Cohort:
        output_value = table("clinical_events").get("code")

    column_definitions = get_column_definitions(Cohort)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=mock_backend(database_url=None)
    )

    sql = query_engine.get_sql()
    assert (
        sql == "SELECT * INTO group_table_0 FROM (\n"
        "SELECT clinical_events.code, clinical_events.patient_id \n"
        "FROM (SELECT EventCode AS code, Date AS date, PatientId AS patient_id \n"
        "FROM events) AS clinical_events\n) t\n\n\n"
        "SELECT * INTO group_table_1 FROM (\n"
        "SELECT practice_registrations.patient_id, 1 AS patient_id_exists \n"
        "FROM (SELECT PatientId AS patient_id \n"
        "FROM practice_registrations) AS practice_registrations GROUP BY practice_registrations.patient_id\n) t\n\n\n"
        "SELECT group_table_1.patient_id AS patient_id, group_table_0.code AS output_value \n"
        "FROM group_table_1 LEFT OUTER JOIN group_table_0 ON group_table_1.patient_id = group_table_0.patient_id \n"
        "WHERE group_table_1.patient_id_exists = 1"
    )


@pytest.mark.integration
def test_run_generated_sql_get_single_column_default_population(
    database, setup_test_database, mock_backend
):

    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        Events(PatientId=1, EventCode="Code1"),
        Events(PatientId=2, EventCode="Code2"),
    ]
    setup_test_database(input_data)

    # Cohort to extract all clinical events and return just the code column
    # Note that the RegistrationHistory table is used for the default population query
    # It will join the two tables on patient_id and only rows that exist in the RegistrationHistory
    # table will be returned
    class Cohort:
        output_value = table("clinical_events").get("code")

    column_definitions = get_column_definitions(Cohort)

    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=mock_backend(database.host_url())
    )
    with query_engine.execute_query() as result:
        assert list(result) == [(1, "Code1")]


@pytest.mark.integration
def test_run_generated_sql_get_single_column_specified_population(
    database, setup_test_database, mock_backend
):
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        Events(PatientId=1, EventCode="Code1"),
        Events(PatientId=2, EventCode="Code2"),
    ]
    setup_test_database(input_data)

    # Cohort to extract all clinical events and return just the code column
    # Note that the RegistrationHistory table is used for the default population query
    # It will join the two tables on patient_id and only rows that exist in the RegistrationHistory
    # table will be returned
    class Cohort:
        output_value = table("clinical_events").get("code")
        population = table("practice_registrations").exists()

    column_definitions = get_column_definitions(Cohort)

    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=mock_backend(database.host_url())
    )
    with query_engine.execute_query() as result:
        assert list(result) == [(1, "Code1")]


@pytest.mark.integration
def test_run_generated_sql_get_multiple_columns(
    database, setup_test_database, mock_backend
):
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        Events(PatientId=1, EventCode="Code1"),
        Events(PatientId=2, EventCode="Code2"),
        PositiveTests(PatientId=1, PositiveResult=True),
        PositiveTests(PatientId=2, PositiveResult=True),
        PositiveTests(PatientId=2, PositiveResult=False),
    ]
    setup_test_database(input_data)

    # Cohort to extract all clinical events and positive tests
    class Cohort:
        output_value = table("clinical_events").get("code")
        positive = table("positive_tests").get("result")

    column_definitions = get_column_definitions(Cohort)

    backend_tables = {
        **DEFAULT_TABLES,
        "positive_tests": SQLTable(
            source="pos_tests",
            columns=dict(result=Column("bool", source="PositiveResult")),
        ),
    }
    backend = mock_backend(database.host_url(), tables=backend_tables)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=backend
    )
    with query_engine.execute_query() as result:
        assert list(result) == [
            (1, "Code1", True),
            (2, "Code2", True),
            (2, "Code2", False),
        ]


@pytest.mark.integration
def test_extract_get_single_column(database, setup_test_database, mock_backend):
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        Events(PatientId=1, EventCode="Code1"),
        Events(PatientId=2, EventCode="Code2"),
    ]
    setup_test_database(input_data)

    # Cohort to extract all clinical events and return just the code column
    # Note that the RegistrationHistory table is used for the default population query
    # It will join the two tables on patient_id and only rows that exist in the RegistrationHistory
    # table will be returned
    class Cohort:
        output_value = table("clinical_events").get("code")

    result = extract(Cohort, mock_backend(database.host_url()))
    assert list(result) == [{"patient_id": 1, "output_value": "Code1"}]


def test_invalid_table(mock_backend):
    class Cohort:
        output_value = table("unknown").get("code")

    column_definitions = get_column_definitions(Cohort)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=mock_backend(database_url=None)
    )
    with pytest.raises(ValueError, match="Unknown table 'unknown'"):
        query_engine.get_sql()


@pytest.mark.integration
@pytest.mark.parametrize(
    "code_output,date_output,expected",
    [
        (
            table("clinical_events").latest().get("code"),
            table("clinical_events").latest().get("date"),
            [(1, "Code2", "2021-5-2"), (2, "Code1", "2021-6-5")],
        ),
        (
            table("clinical_events").earliest().get("code"),
            table("clinical_events").earliest().get("date"),
            [(1, "Code1", "2021-1-3"), (2, "Code1", "2021-2-4")],
        ),
    ],
)
def test_run_generated_sql_get_single_row_per_patient(
    database, setup_test_database, mock_backend, code_output, date_output, expected
):
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        Events(PatientId=1, EventCode="Code1", Date="2021-1-3"),
        Events(PatientId=1, EventCode="Code1", Date="2021-2-1"),
        Events(PatientId=1, EventCode="Code2", Date="2021-5-2"),
        Events(PatientId=2, EventCode="Code1", Date="2021-6-5"),
        Events(PatientId=2, EventCode="Code1", Date="2021-2-4"),
    ]
    setup_test_database(input_data)

    # Cohort to extract the earliest/latest event for each patient, and return code and date
    class Cohort:
        code_value = code_output
        date_value = date_output

    column_definitions = get_column_definitions(Cohort)

    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=mock_backend(database.host_url())
    )
    with query_engine.execute_query() as result:
        assert list(result) == expected
