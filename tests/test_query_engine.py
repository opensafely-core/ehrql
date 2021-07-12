from datetime import date

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


DEFAULT_TABLES = {
    "practice_registrations": SQLTable(
        source="practice_registrations",
        columns=dict(
            patient_id=Column("int", source="PatientId"),
            stp=Column("varchar", source="StpId"),
            date_start=Column("date", source="StartDate"),
            date_end=Column("date", source="EndDate"),
        ),
    ),
    "clinical_events": SQLTable(
        source="events",
        columns=dict(
            code=Column("varchar", source="EventCode"),
            date=Column("date", source="Date"),
            result=Column("float", source="ResultValue"),
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
def setup_test_database(database):
    db_url = database.host_url()

    def setup(input_data, drivername="mssql+pymssql"):
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
            [(1, "Code2", date(2021, 5, 2)), (2, "Code1", date(2021, 6, 5))],
        ),
        (
            table("clinical_events").earliest().get("code"),
            table("clinical_events").earliest().get("date"),
            [(1, "Code1", date(2021, 1, 3)), (2, "Code1", date(2021, 2, 4))],
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


@pytest.mark.integration
@pytest.mark.parametrize(
    "filtered_table,expected",
    [
        (
            table("clinical_events").filter(code="Code1"),
            [
                (1, "Code1", date(2021, 1, 3), 10.1),
                (1, "Code1", date(2021, 2, 1), 20.1),
                (2, "Code1", date(2021, 6, 5), 50.1),
            ],
        ),
        (
            table("clinical_events").filter(code="Code1", date="2021-2-1"),
            [(1, "Code1", date(2021, 2, 1), 20.1), (2, None, None, None)],
        ),
        (
            table("clinical_events").filter("date", between=["2021-1-15", "2021-5-3"]),
            [
                (1, "Code1", date(2021, 2, 1), 20.1),
                (1, "Code2", date(2021, 5, 2), 30.1),
                (1, "Code3", date(2021, 5, 3), 40.1),
                (2, "Code2", date(2021, 2, 1), 60.1),
            ],
        ),
        (
            table("clinical_events").filter("result", greater_than=40),
            [
                (1, "Code3", date(2021, 5, 3), 40.1),
                (2, "Code1", date(2021, 6, 5), 50.1),
                (2, "Code2", date(2021, 2, 1), 60.1),
            ],
        ),
        (
            table("clinical_events").filter("date", greater_than="2021-5-3"),
            [(1, None, None, None), (2, "Code1", date(2021, 6, 5), 50.1)],
        ),
        (
            table("clinical_events").filter("date", greater_than_or_equals="2021-5-3"),
            [
                (1, "Code3", date(2021, 5, 3), 40.1),
                (2, "Code1", date(2021, 6, 5), 50.1),
            ],
        ),
        (
            table("clinical_events").filter("date", on_or_after="2021-5-3"),
            [
                (1, "Code3", date(2021, 5, 3), 40.1),
                (2, "Code1", date(2021, 6, 5), 50.1),
            ],
        ),
        (
            table("clinical_events").filter("date", less_than="2021-2-1"),
            [(1, "Code1", date(2021, 1, 3), 10.1), (2, None, None, None)],
        ),
        (
            table("clinical_events").filter("date", less_than_or_equals="2021-2-1"),
            [
                (1, "Code1", date(2021, 1, 3), 10.1),
                (1, "Code1", date(2021, 2, 1), 20.1),
                (2, "Code2", date(2021, 2, 1), 60.1),
            ],
        ),
        (
            table("clinical_events").filter("date", on_or_before="2021-2-1"),
            [
                (1, "Code1", date(2021, 1, 3), 10.1),
                (1, "Code1", date(2021, 2, 1), 20.1),
                (2, "Code2", date(2021, 2, 1), 60.1),
            ],
        ),
        (
            table("clinical_events").filter("result", less_than_or_equals=20.2),
            [
                (1, "Code1", date(2021, 1, 3), 10.1),
                (1, "Code1", date(2021, 2, 1), 20.1),
                (2, None, None, None),
            ],
        ),
        (
            table("clinical_events").filter("code", not_equals="Code1"),
            [
                (1, "Code2", date(2021, 5, 2), 30.1),
                (1, "Code3", date(2021, 5, 3), 40.1),
                (2, "Code2", date(2021, 2, 1), 60.1),
            ],
        ),
        (
            table("clinical_events").filter("code", is_in=["Code2", "Code3"]),
            [
                (1, "Code2", date(2021, 5, 2), 30.1),
                (1, "Code3", date(2021, 5, 3), 40.1),
                (2, "Code2", date(2021, 2, 1), 60.1),
            ],
        ),
        (
            table("clinical_events").filter("code", not_in=["Code1", "Code2"]),
            [
                (1, "Code3", date(2021, 5, 3), 40.1),
                (2, None, None, None),
            ],
        ),
        (
            table("clinical_events")
            .filter(code="Code1")
            .filter("result", less_than=50)
            .filter("date", between=["2021-1-15", "2021-6-6"]),
            [(1, "Code1", date(2021, 2, 1), 20.1), (2, None, None, None)],
        ),
    ],
    ids=[
        "test single equals filter",
        "test multiple equals filter",
        "test between filter",
        "test greater than filter on numeric data",
        "test greater than filter on date data",
        "test greater than or equals filter on date data",
        "test on or after filter (alias for gte)",
        "test less than filter on date data",
        "test less than or equals filter on date data",
        "test on or before filter (alias for lte)",
        "test less than or equals filter on numeric data",
        "test not equals filter",
        "test in filter",
        "test not in filter",
        "test multiple chained filters",
    ],
)
def test_simple_filters(
    database, setup_test_database, mock_backend, filtered_table, expected
):
    """Test the filters on simple value comparisons"""
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        Events(PatientId=1, EventCode="Code1", Date="2021-1-3", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", Date="2021-2-1", ResultValue=20.1),
        Events(PatientId=1, EventCode="Code2", Date="2021-5-2", ResultValue=30.1),
        Events(PatientId=1, EventCode="Code3", Date="2021-5-3", ResultValue=40.1),
        Events(PatientId=2, EventCode="Code1", Date="2021-6-5", ResultValue=50.1),
        Events(PatientId=2, EventCode="Code2", Date="2021-2-1", ResultValue=60.1),
    ]
    setup_test_database(input_data)

    class Cohort:
        _filtered = filtered_table
        code = _filtered.get("code")
        date = _filtered.get("date")
        value = _filtered.get("result")

    column_definitions = get_column_definitions(Cohort)

    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=mock_backend(database.host_url())
    )
    with query_engine.execute_query() as result:
        assert list(result) == expected


@pytest.mark.integration
def test_filter_between_other_query_values(database, setup_test_database, mock_backend):
    # set up input data for 3 patients, with positive test dates and clinical event results
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        RegistrationHistory(PatientId=3, StpId="STP1"),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-1-1"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-2-15"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-3-2"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-1-21"),
        PositiveTests(PatientId=2, PositiveResult=False, TestDate="2021-2-17"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-5-1"),
        PositiveTests(PatientId=3, PositiveResult=True, TestDate="2021-1-10"),
        PositiveTests(PatientId=3, PositiveResult=True, TestDate="2021-2-23"),
        PositiveTests(PatientId=3, PositiveResult=True, TestDate="2021-3-1"),
        # pt1 first=2021-1-1, last=2021-3-2; 2 values between dates, 1 outside
        Events(PatientId=1, EventCode="Code1", Date="2021-2-1", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", Date="2021-4-12", ResultValue=10.2),
        Events(
            PatientId=1, EventCode="Code1", Date="2021-3-1", ResultValue=10.3
        ),  # selected
        # pt2 first=2021-1-21, last=2021-5-1, 1 between, 2 outside
        Events(PatientId=2, EventCode="Code1", Date="2021-1-10", ResultValue=50.1),
        Events(
            PatientId=2, EventCode="Code1", Date="2021-2-1", ResultValue=50.2
        ),  # selected
        Events(PatientId=2, EventCode="Code1", Date="2021-5-2", ResultValue=50.3),
        # pt3 first=2021-1-10, last=2021-3-1, none inside
        Events(PatientId=3, EventCode="Code1", Date="2021-3-15", ResultValue=60.1),
        Events(PatientId=3, EventCode="Code1", Date="2021-4-1", ResultValue=60.1),
        # within dates, but different code
        Events(PatientId=3, EventCode="Code2", Date="2021-2-1", ResultValue=60.1),
    ]
    setup_test_database(input_data)

    backend_tables = {
        **DEFAULT_TABLES,
        "positive_tests": SQLTable(
            source="pos_tests",
            columns=dict(
                result=Column("bool", source="PositiveResult"),
                test_date=Column("date", source="TestDate"),
            ),
        ),
    }

    # Cohort to extract the last Code1 result between a patient's first and last positive test dates
    class Cohort:
        _positive_tests = table("positive_tests").filter(result=True)
        first_pos = _positive_tests.earliest("test_date").get("test_date")
        last_pos = _positive_tests.latest("test_date").get("test_date")
        _events = (
            table("clinical_events")
            .filter(code="Code1")
            .filter("date", between=[first_pos, last_pos])
            .latest()
        )
        date = _events.get("date")
        value = _events.get("result")

    backend = mock_backend(database.host_url(), tables=backend_tables)

    result = list(extract(Cohort, backend))
    assert result == [
        {
            "patient_id": 1,
            "date": date(2021, 3, 1),
            "first_pos": date(2021, 1, 1),
            "last_pos": date(2021, 3, 2),
            "value": 10.3,
        },
        {
            "patient_id": 2,
            "date": date(2021, 2, 1),
            "first_pos": date(2021, 1, 21),
            "last_pos": date(2021, 5, 1),
            "value": 50.2,
        },
        {
            "patient_id": 3,
            "date": None,
            "first_pos": date(2021, 1, 10),
            "last_pos": date(2021, 3, 1),
            "value": None,
        },
    ]


@pytest.mark.integration
def test_date_in_range_filter(database, setup_test_database, mock_backend):
    input_data = [
        # (9999-12-31 is the default TPP null value)
        # registraion start date before target date; no end date - included
        RegistrationHistory(
            PatientId=1, StpId="STP1", StartDate="2021-1-2", EndDate="9999-12-31"
        ),
        # registration starts after target date; no end date - not included
        RegistrationHistory(
            PatientId=2, StpId="STP2", StartDate="2021-3-3", EndDate="9999-12-31"
        ),
        # 2 registrations, not overlapping; include the one that contains the target date
        RegistrationHistory(
            PatientId=3, StpId="STP1", StartDate="2021-2-2", EndDate="2021-3-1"
        ),
        RegistrationHistory(
            PatientId=3, StpId="STP2", StartDate="2021-3-1", EndDate="2021-4-1"
        ),
        # registered with 2 STPs overlapping target date; latest included
        RegistrationHistory(
            PatientId=4, StpId="STP2", StartDate="2021-2-2", EndDate="2021-4-1"
        ),
        RegistrationHistory(
            PatientId=4, StpId="STP3", StartDate="2021-1-1", EndDate="2021-3-3"
        ),
        # Patient test results with dates
        Events(PatientId=1, EventCode="Code1", Date="2021-3-1", ResultValue=10.1),
        Events(PatientId=2, EventCode="Code1", Date="2021-3-1", ResultValue=10.2),
        Events(PatientId=3, EventCode="Code1", Date="2021-3-1", ResultValue=10.3),
        Events(PatientId=4, EventCode="Code1", Date="2021-3-1", ResultValue=10.4),
    ]
    setup_test_database(input_data)

    class Cohort:
        _events = table("clinical_events").latest()
        value = _events.get("result")
        stp = table("practice_registrations").date_in_range("2021-3-2").get("stp")

    result = list(extract(Cohort, mock_backend(database.host_url())))
    assert result == [
        {"patient_id": 1, "value": 10.1, "stp": "STP1"},
        {"patient_id": 2, "value": 10.2, "stp": None},
        {"patient_id": 3, "value": 10.3, "stp": "STP2"},
        {"patient_id": 4, "value": 10.4, "stp": "STP2"},
    ]


@pytest.mark.integration
def test_in_filter_on_query_values(database, setup_test_database, mock_backend):
    # set up input data for 2 patients, with positive test dates and clinical event results
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-1-1"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-2-15"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-3-2"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-1-10"),
        PositiveTests(PatientId=2, PositiveResult=False, TestDate="2021-2-1"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-5-1"),
        # pt1 2 results with dates matching a positive result: SELECTED
        Events(PatientId=1, EventCode="Code1", Date="2021-1-1", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", Date="2021-2-15", ResultValue=10.2),
        # pt1 1 result that doesn't match a positive result date
        Events(PatientId=1, EventCode="Code1", Date="2021-5-1", ResultValue=10.3),
        # pt2 1 result matches a positive result date: SELECTED
        Events(PatientId=2, EventCode="Code1", Date="2021-1-10", ResultValue=50.1),
        # pt2 1 matches a negative result date
        Events(PatientId=2, EventCode="Code1", Date="2021-2-1", ResultValue=50.2),
        # pt2 1 result matches a positive result date but a different code
        Events(PatientId=2, EventCode="Code2", Date="2021-5-1", ResultValue=50.3),
    ]
    setup_test_database(input_data)

    backend_tables = {
        **DEFAULT_TABLES,
        "positive_tests": SQLTable(
            source="pos_tests",
            columns=dict(
                positive_result=Column("bool", source="PositiveResult"),
                test_date=Column("date", source="TestDate"),
            ),
        ),
    }

    # Cohort to extract the Code1 results that were on a positive test date
    class Cohort:
        _positive_test_dates = (
            table("positive_tests").filter(positive_result=True).get("test_date")
        )
        _last_code1_events_on_positive_test_dates = (
            table("clinical_events")
            .filter(code="Code1")
            .filter("date", is_in=_positive_test_dates)
            .latest()
        )
        date = _last_code1_events_on_positive_test_dates.get("date")
        value = _last_code1_events_on_positive_test_dates.get("result")

    backend = mock_backend(database.host_url(), tables=backend_tables)

    result = list(extract(Cohort, backend))
    expected = [
        {"patient_id": 1, "date": date(2021, 2, 15), "value": 10.2},
        {"patient_id": 2, "date": date(2021, 1, 10), "value": 50.1},
    ]
    assert result == expected


@pytest.mark.integration
def test_not_in_filter_on_query_values(database, setup_test_database, mock_backend):
    # set up input data for 2 patients, with positive test dates and clinical event results
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-1-1"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-2-15"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-3-2"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-5-1"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-1-10"),
        PositiveTests(PatientId=2, PositiveResult=False, TestDate="2021-2-1"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-5-1"),
        # pt1 2 results with dates matching a positive result
        Events(PatientId=1, EventCode="Code1", Date="2021-1-1", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", Date="2021-2-15", ResultValue=10.2),
        # pt1 1 result that doesn't match a positive result date: SELECTED
        Events(PatientId=1, EventCode="Code1", Date="2021-4-1", ResultValue=10.3),
        # pt2 1 result matches a positive result date
        Events(PatientId=2, EventCode="Code1", Date="2021-1-10", ResultValue=50.1),
        # pt2 1 matches a negative result date
        Events(PatientId=2, EventCode="Code1", Date="2021-2-1", ResultValue=50.2),
        # pt2 1 result doesn't match any result date: SELECTED
        Events(PatientId=2, EventCode="Code1", Date="2021-5-2", ResultValue=50.3),
    ]
    setup_test_database(input_data)

    backend_tables = {
        **DEFAULT_TABLES,
        "positive_tests": SQLTable(
            source="pos_tests",
            columns=dict(
                positive_result=Column("bool", source="PositiveResult"),
                test_date=Column("date", source="TestDate"),
            ),
        ),
    }

    # Cohort to extract the results that were NOT on a test date (positive or negative)
    class Cohort:
        _test_dates = table("positive_tests").get("test_date")
        _last_event_not_on_test_date = (
            table("clinical_events").filter("date", not_in=_test_dates).latest()
        )
        date = _last_event_not_on_test_date.get("date")
        value = _last_event_not_on_test_date.get("result")

    backend = mock_backend(database.host_url(), tables=backend_tables)

    result = list(extract(Cohort, backend))
    expected = [
        {"patient_id": 1, "date": date(2021, 4, 1), "value": 10.3},
        {"patient_id": 2, "date": date(2021, 5, 2), "value": 50.3},
    ]
    assert result == expected
