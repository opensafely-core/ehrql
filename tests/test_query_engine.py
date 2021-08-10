from datetime import date

import pytest
from lib.databases import null_database
from lib.mock_backend import (
    Events,
    MockBackend,
    Patients,
    PositiveTests,
    RegistrationHistory,
    event,
    patient,
)
from lib.util import extract, mark_xfail_in_playback_mode

from cohortextractor.query_language import categorise, table


def test_backend_tables():
    """Test that a backend registers its table names"""
    assert MockBackend.tables == {
        "practice_registrations",
        "clinical_events",
        "patients",
        "positive_tests",
    }


@pytest.mark.integration
def test_run_generated_sql_get_single_column_default_population(
    database, setup_test_database
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
        output_value = table("clinical_events").first_by("patient_id").get("code")

    assert extract(Cohort, MockBackend, database) == [
        dict(patient_id=1, output_value="Code1")
    ]


@pytest.mark.integration
def test_run_generated_sql_get_single_column_specified_population(
    database, setup_test_database
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
        output_value = table("clinical_events").first_by("patient_id").get("code")
        population = table("practice_registrations").exists()

    assert extract(Cohort, MockBackend, database) == [
        dict(patient_id=1, output_value="Code1")
    ]


@pytest.mark.integration
def test_run_generated_sql_get_multiple_columns(database, setup_test_database):
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
        output_value = table("clinical_events").first_by("patient_id").get("code")
        positive = table("positive_tests").first_by("patient_id").get("result")

    assert extract(Cohort, MockBackend, database) == [
        dict(patient_id=1, output_value="Code1", positive=True),
        dict(patient_id=2, output_value="Code2", positive=False),
    ]


@pytest.mark.integration
def test_extract_get_single_column(database, setup_test_database):
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
        output_value = table("clinical_events").first_by("patient_id").get("code")

    result = extract(Cohort, MockBackend, database)
    assert list(result) == [dict(patient_id=1, output_value="Code1")]


def test_invalid_table():
    class Cohort:
        output_value = table("unknown").first_by("patient_id").get("code")

    with pytest.raises(ValueError, match="Unknown table 'unknown'"):
        extract(Cohort, MockBackend, null_database())


@pytest.mark.integration
@pytest.mark.parametrize(
    "code_output,date_output,expected",
    [
        (
            table("clinical_events").latest().get("code"),
            table("clinical_events").latest().get("date"),
            [
                dict(patient_id=1, code="Code2", date=date(2021, 5, 2)),
                dict(patient_id=2, code="Code1", date=date(2021, 6, 5)),
            ],
        ),
        (
            table("clinical_events").earliest().get("code"),
            table("clinical_events").earliest().get("date"),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 3)),
                dict(patient_id=2, code="Code1", date=date(2021, 2, 4)),
            ],
        ),
    ],
)
def test_run_generated_sql_get_single_row_per_patient(
    database, setup_test_database, code_output, date_output, expected
):
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        Events(PatientId=1, EventCode="Code1", Date="2021-01-03"),
        Events(PatientId=1, EventCode="Code1", Date="2021-02-01"),
        Events(PatientId=1, EventCode="Code2", Date="2021-05-02"),
        Events(PatientId=2, EventCode="Code1", Date="2021-06-05"),
        Events(PatientId=2, EventCode="Code1", Date="2021-02-04"),
    ]
    setup_test_database(input_data)

    # Cohort to extract the earliest/latest event for each patient, and return code and date
    class Cohort:
        code = code_output
        date = date_output

    assert extract(Cohort, MockBackend, database) == expected


@pytest.mark.integration
@pytest.mark.parametrize(
    "data,filtered_table,expected",
    [
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # equal
                *patient(2, event("Code2", "2021-02-02", 20)),  # not equal
            ],
            table("clinical_events").filter(code="Code1"),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # both equal
                *patient(2, event("Code1", "2021-01-02", 20)),  # only one equal
            ],
            table("clinical_events").filter(code="Code1", date="2021-01-01"),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # before
                *patient(2, event("Code2", "2021-01-02", 20)),  # start of range
                *patient(3, event("Code3", "2021-01-03", 30)),  # within range
                *patient(4, event("Code4", "2021-01-04", 40)),  # end of range
                *patient(5, event("Code5", "2021-01-05", 50)),  # after
            ],
            table("clinical_events").filter(
                "date", between=["2021-01-02", "2021-01-04"]
            ),
            [
                dict(patient_id=2, code="Code2", date=date(2021, 1, 2), value=20),
                dict(patient_id=3, code="Code3", date=date(2021, 1, 3), value=30),
                dict(patient_id=4, code="Code4", date=date(2021, 1, 4), value=40),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # less than
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
                *patient(3, event("Code3", "2021-01-03", 30)),  # greater than
            ],
            table("clinical_events").filter("result", greater_than=20),
            [
                dict(patient_id=3, code="Code3", date=date(2021, 1, 3), value=30),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # less than
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
                *patient(3, event("Code3", "2021-01-03", 30)),  # greater than
            ],
            table("clinical_events").filter("date", greater_than="2021-01-02"),
            [
                dict(patient_id=3, code="Code3", date=date(2021, 1, 3), value=30),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # less than
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
                *patient(3, event("Code3", "2021-01-03", 30)),  # greater than
            ],
            table("clinical_events").filter(
                "date", greater_than_or_equals="2021-01-02"
            ),
            [
                dict(patient_id=2, code="Code2", date=date(2021, 1, 2), value=20),
                dict(patient_id=3, code="Code3", date=date(2021, 1, 3), value=30),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # less than
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
                *patient(3, event("Code3", "2021-01-03", 30)),  # greater than
            ],
            table("clinical_events").filter("date", on_or_after="2021-01-02"),
            [
                dict(patient_id=2, code="Code2", date=date(2021, 1, 2), value=20),
                dict(patient_id=3, code="Code3", date=date(2021, 1, 3), value=30),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # less than
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
                *patient(3, event("Code3", "2021-01-03", 30)),  # greater than
            ],
            table("clinical_events").filter("date", less_than="2021-01-02"),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # less than
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
                *patient(3, event("Code3", "2021-01-03", 30)),  # greater than
            ],
            table("clinical_events").filter("date", less_than_or_equals="2021-01-02"),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
                dict(patient_id=2, code="Code2", date=date(2021, 1, 2), value=20),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # before
                *patient(2, event("Code2", "2021-01-02", 20)),  # on
                *patient(3, event("Code3", "2021-01-03", 30)),  # after
            ],
            table("clinical_events").filter("date", on_or_before="2021-01-02"),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
                dict(patient_id=2, code="Code2", date=date(2021, 1, 2), value=20),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # less than
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
                *patient(3, event("Code3", "2021-01-03", 30)),  # greater than
            ],
            table("clinical_events").filter("result", less_than_or_equals=20),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
                dict(patient_id=2, code="Code2", date=date(2021, 1, 2), value=20),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # not equal
                *patient(2, event("Code2", "2021-01-02", 20)),  # equal
            ],
            table("clinical_events").filter("code", not_equals="Code2"),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # in
                *patient(2, event("Code2", "2021-01-02", 20)),  # not in
            ],
            table("clinical_events").filter("code", is_in=["Code1", "Code999"]),
            [
                dict(patient_id=1, code="Code1", date=date(2021, 1, 1), value=10),
            ],
        ),
        (
            [
                *patient(1, event("Code1", "2021-01-01", 10)),  # in
                *patient(2, event("Code2", "2021-01-02", 20)),  # not in
            ],
            table("clinical_events").filter("code", not_in=["Code1", "Code999"]),
            [
                dict(patient_id=2, code="Code2", date=date(2021, 1, 2), value=20),
            ],
        ),
        (
            [
                *patient(
                    1, event("Code1", "2021-01-01", 10)
                ),  # excluded by first filter
                *patient(
                    2, event("Code2", "2021-01-02", 20)
                ),  # excluded by second filter
                *patient(
                    3, event("Code3", "2021-01-03", 30)
                ),  # excluded by third filter
                *patient(4, event("Code4", "2021-01-04", 40)),  # included
            ],
            table("clinical_events")
            .filter("result", greater_than=15)
            .filter("date", between=["2021-01-03", "2021-06-06"])
            .filter(code="Code4"),
            [
                dict(patient_id=4, code="Code4", date=date(2021, 1, 4), value=40),
            ],
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
def test_simple_filters(database, setup_test_database, data, filtered_table, expected):
    setup_test_database(data)

    class Cohort:
        population = filtered_table.exists()
        _filtered = filtered_table.first_by("patient_id")
        code = _filtered.get("code")
        date = _filtered.get("date")
        value = _filtered.get("result")

    assert extract(Cohort, MockBackend, database) == expected


@pytest.mark.integration
def test_filter_between_other_query_values(database, setup_test_database):
    # set up input data for 3 patients, with positive test dates and clinical event results
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        RegistrationHistory(PatientId=3, StpId="STP1"),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-01-01"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-02-15"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-03-02"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-01-21"),
        PositiveTests(PatientId=2, PositiveResult=False, TestDate="2021-02-17"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-05-01"),
        PositiveTests(PatientId=3, PositiveResult=True, TestDate="2021-01-10"),
        PositiveTests(PatientId=3, PositiveResult=True, TestDate="2021-02-23"),
        PositiveTests(PatientId=3, PositiveResult=True, TestDate="2021-03-01"),
        # pt1 first=2021-01-01, last=2021-03-02; 2 values between dates, 1 outside
        Events(PatientId=1, EventCode="Code1", Date="2021-02-01", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", Date="2021-04-12", ResultValue=10.2),
        Events(
            PatientId=1, EventCode="Code1", Date="2021-03-01", ResultValue=10.3
        ),  # selected
        # pt2 first=2021-01-21, last=2021-05-01, 1 between, 2 outside
        Events(PatientId=2, EventCode="Code1", Date="2021-01-10", ResultValue=50.1),
        Events(
            PatientId=2, EventCode="Code1", Date="2021-02-01", ResultValue=50.2
        ),  # selected
        Events(PatientId=2, EventCode="Code1", Date="2021-05-02", ResultValue=50.3),
        # pt3 first=2021-01-10, last=2021-03-01, none inside
        Events(PatientId=3, EventCode="Code1", Date="2021-03-15", ResultValue=60.1),
        Events(PatientId=3, EventCode="Code1", Date="2021-04-01", ResultValue=60.1),
        # within dates, but different code
        Events(PatientId=3, EventCode="Code2", Date="2021-02-01", ResultValue=60.1),
    ]
    setup_test_database(input_data)

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

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(
            patient_id=1,
            date=date(2021, 3, 1),
            first_pos=date(2021, 1, 1),
            last_pos=date(2021, 3, 2),
            value=10.3,
        ),
        dict(
            patient_id=2,
            date=date(2021, 2, 1),
            first_pos=date(2021, 1, 21),
            last_pos=date(2021, 5, 1),
            value=50.2,
        ),
        dict(
            patient_id=3,
            date=None,
            first_pos=date(2021, 1, 10),
            last_pos=date(2021, 3, 1),
            value=None,
        ),
    ]


@pytest.mark.integration
def test_date_in_range_filter(database, setup_test_database):
    input_data = [
        # (9999-12-31 is the default TPP null value)
        # registraion start date before target date; no end date - included
        RegistrationHistory(
            PatientId=1, StpId="STP1", StartDate="2021-01-02", EndDate="9999-12-31"
        ),
        # registration starts after target date; no end date - not included
        RegistrationHistory(
            PatientId=2, StpId="STP2", StartDate="2021-03-03", EndDate="9999-12-31"
        ),
        # 2 registrations, not overlapping; include the one that contains the target date
        RegistrationHistory(
            PatientId=3, StpId="STP1", StartDate="2021-02-02", EndDate="2021-03-01"
        ),
        RegistrationHistory(
            PatientId=3, StpId="STP2", StartDate="2021-03-01", EndDate="2021-04-01"
        ),
        # registered with 2 STPs overlapping target date; both are included
        RegistrationHistory(
            PatientId=4, StpId="STP2", StartDate="2021-02-02", EndDate="2021-04-01"
        ),
        RegistrationHistory(
            PatientId=4, StpId="STP3", StartDate="2021-01-01", EndDate="2021-03-03"
        ),
    ]
    setup_test_database(input_data)

    class Cohort:
        _registrations = table("practice_registrations").date_in_range("2021-03-02")
        stp = _registrations.first_by("patient_id").get("stp")
        count = _registrations.count("patient_id")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, stp="STP1", count=1),
        dict(patient_id=2, stp=None, count=None),
        dict(patient_id=3, stp="STP2", count=1),
        dict(patient_id=4, stp="STP2", count=2),
    ]


@pytest.mark.integration
def test_in_filter_on_query_values(database, setup_test_database):
    # set up input data for 2 patients, with positive test dates and clinical event results
    input_data = [
        RegistrationHistory(PatientId=1, StpId="STP1"),
        RegistrationHistory(PatientId=2, StpId="STP1"),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-01-01"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-02-15"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-03-02"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-01-10"),
        PositiveTests(PatientId=2, PositiveResult=False, TestDate="2021-02-01"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-05-01"),
        # pt1 2 results with dates matching a positive result: SELECTED
        Events(PatientId=1, EventCode="Code1", Date="2021-01-01", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", Date="2021-02-15", ResultValue=10.2),
        # pt1 1 result that doesn't match a positive result date
        Events(PatientId=1, EventCode="Code1", Date="2021-05-01", ResultValue=10.3),
        # pt2 1 result matches a positive result date: SELECTED
        Events(PatientId=2, EventCode="Code1", Date="2021-01-10", ResultValue=50.1),
        # pt2 1 matches a negative result date
        Events(PatientId=2, EventCode="Code1", Date="2021-02-01", ResultValue=50.2),
        # pt2 1 result matches a positive result date but a different code
        Events(PatientId=2, EventCode="Code2", Date="2021-05-01", ResultValue=50.3),
    ]
    setup_test_database(input_data)

    # Cohort to extract the Code1 results that were on a positive test date
    class Cohort:
        _positive_test_dates = (
            table("positive_tests").filter(result=True).get("test_date")
        )
        _last_code1_events_on_positive_test_dates = (
            table("clinical_events")
            .filter(code="Code1")
            .filter("date", is_in=_positive_test_dates)
            .latest()
        )
        date = _last_code1_events_on_positive_test_dates.get("date")
        value = _last_code1_events_on_positive_test_dates.get("result")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, date=date(2021, 2, 15), value=10.2),
        dict(patient_id=2, date=date(2021, 1, 10), value=50.1),
    ]


@pytest.mark.integration
def test_not_in_filter_on_query_values(database, setup_test_database):
    # set up input data for 2 patients, with positive test dates and clinical event results
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-01-01"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-02-15"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-03-02"),
        PositiveTests(PatientId=1, PositiveResult=True, TestDate="2021-05-01"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-01-10"),
        PositiveTests(PatientId=2, PositiveResult=False, TestDate="2021-02-01"),
        PositiveTests(PatientId=2, PositiveResult=True, TestDate="2021-05-01"),
        # pt1 2 results with dates matching a positive result
        Events(PatientId=1, EventCode="Code1", Date="2021-01-01", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", Date="2021-02-15", ResultValue=10.2),
        # pt1 1 result that doesn't match a positive result date: SELECTED
        Events(PatientId=1, EventCode="Code1", Date="2021-04-01", ResultValue=10.3),
        # pt2 1 result matches a positive result date
        Events(PatientId=2, EventCode="Code1", Date="2021-01-10", ResultValue=50.1),
        # pt2 1 matches a negative result date
        Events(PatientId=2, EventCode="Code1", Date="2021-02-01", ResultValue=50.2),
        # pt2 1 result doesn't match any result date: SELECTED
        Events(PatientId=2, EventCode="Code1", Date="2021-05-02", ResultValue=50.3),
    ]
    setup_test_database(input_data)

    # Cohort to extract the results that were NOT on a test date (positive or negative)
    class Cohort:
        _test_dates = table("positive_tests").get("test_date")
        _last_event_not_on_test_date = (
            table("clinical_events").filter("date", not_in=_test_dates).latest()
        )
        date = _last_event_not_on_test_date.get("date")
        value = _last_event_not_on_test_date.get("result")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, date=date(2021, 4, 1), value=10.3),
        dict(patient_id=2, date=date(2021, 5, 2), value=50.3),
    ]


@pytest.mark.integration
@pytest.mark.parametrize(
    "aggregation,column,expected",
    [
        (
            "exists",
            "code",
            [
                dict(patient_id=1, value=True),
                dict(patient_id=2, value=True),
                dict(patient_id=3, value=None),
            ],
        ),
        (
            "count",
            "code",
            [
                dict(patient_id=1, value=2),
                dict(patient_id=2, value=1),
                dict(patient_id=3, value=None),
            ],
        ),
        (
            "sum",
            "result",
            [
                dict(patient_id=1, value=20.6),
                dict(patient_id=2, value=50.1),
                dict(patient_id=3, value=None),
            ],
        ),
    ],
    ids=[],
)
def test_aggregation(database, setup_test_database, aggregation, column, expected):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        Events(PatientId=1, EventCode="Code1", ResultValue=10.1),
        Events(PatientId=1, EventCode="Code1", ResultValue=10.5),
        Events(PatientId=1, EventCode="Code2", ResultValue=30.1),
        Events(PatientId=2, EventCode="Code1", ResultValue=50.1),
        Events(PatientId=2, EventCode="Code2", ResultValue=60.1),
        Events(PatientId=3, EventCode="Code2", ResultValue=70.1),
    ]
    setup_test_database(input_data)

    class Cohort:
        _filtered_table = table("clinical_events").filter(code="Code1")
        value = getattr(_filtered_table, aggregation)(column)

    assert extract(Cohort, MockBackend, database) == expected


@pytest.mark.integration
def test_categorise_simple_comparisons(database, setup_test_database):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        Patients(PatientId=1, Height=180),
        Patients(PatientId=2, Height=200.5),
        Patients(PatientId=3),
    ]
    setup_test_database(input_data)

    class Cohort:
        _height = table("patients").first_by("patient_id").get("height")
        _height_categories = {
            "tall": _height > 190,
            "short": _height <= 190,
        }
        height_group = categorise(_height_categories, default="missing")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, height_group="short"),
        dict(patient_id=2, height_group="tall"),
        dict(patient_id=3, height_group="missing"),
    ]


@pytest.mark.integration
@pytest.mark.parametrize(
    "categories,default,expected",
    [
        (
            lambda height_value: {
                "tall": height_value > 190,
                "medium": (height_value <= 190) & (height_value > 150),
                "short": height_value < 150,
            },
            "missing",
            [
                dict(patient_id=1, height_group="medium"),
                dict(patient_id=2, height_group="tall"),
                dict(patient_id=3, height_group="missing"),
                dict(patient_id=4, height_group="short"),
            ],
        ),
        (
            lambda height_value: {
                "short_or_tall": (height_value < 150) | (height_value > 190)
            },
            "medium",
            [
                dict(patient_id=1, height_group="medium"),
                dict(patient_id=2, height_group="short_or_tall"),
                dict(patient_id=3, height_group="medium"),
                dict(patient_id=4, height_group="short_or_tall"),
            ],
        ),
        (
            lambda height_value: {
                "tallish": (height_value > 175) & (height_value != 180),
                "short": height_value <= 175,
            },
            "missing",
            [
                dict(patient_id=1, height_group="missing"),
                dict(patient_id=2, height_group="tallish"),
                dict(patient_id=3, height_group="missing"),
                dict(patient_id=4, height_group="short"),
            ],
        ),
    ],
    ids=[
        "test simple and on two conditions",
        "test simple or on two conditions",
        "test a not-equals condition",
    ],
)
def test_categorise_single_combined_conditions(
    database, setup_test_database, categories, default, expected
):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        Patients(PatientId=1, Height=180),
        Patients(PatientId=2, Height=200.5),
        Patients(PatientId=3),
        Patients(PatientId=4, Height=145),
    ]
    setup_test_database(input_data)

    class Cohort:
        _height = table("patients").first_by("patient_id").get("height")
        _height_categories = categories(_height)
        height_group = categorise(_height_categories, default=default)

    result = list(extract(Cohort, MockBackend, database))
    assert result == expected


@pytest.mark.integration
def test_categorise_multiple_values(database, setup_test_database):
    """Test that categories can combine conditions that use different source values"""
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        Patients(PatientId=1, Height=200),
        Patients(PatientId=2, Height=150),
        Patients(PatientId=3, Height=160),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
    ]
    setup_test_database(input_data)

    class Cohort:
        _height = table("patients").first_by("patient_id").get("height")
        _code = table("clinical_events").first_by("patient_id").get("code")
        _height_with_codes_categories = {
            "short": (_height < 190) & (_code == "abc"),
            "tall": (_height > 190) & (_code == "abc"),
        }
        height_group = categorise(_height_with_codes_categories, default="missing")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, height_group="tall"),
        dict(patient_id=2, height_group="missing"),
        dict(patient_id=3, height_group="short"),
    ]


@pytest.mark.integration
def test_categorise_nested_comparisons(database, setup_test_database):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        RegistrationHistory(PatientId=5),
        Patients(PatientId=1, Height=194),  # tall with code - matches
        Patients(PatientId=2, Height=200.5),  # tall no code  - matches
        Patients(PatientId=3, Height=140.5),  # short with code - matches
        Patients(PatientId=4, Height=140.5),  # short no code
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
    ]
    setup_test_database(input_data)

    class Cohort:
        _height = table("patients").first_by("patient_id").get("height")
        _code = table("clinical_events").first_by("patient_id").get("code")

        # make sure the parentheses precedence is followed; these two expressions are equivalent
        _height_with_codes_categories = {
            "tall_or_code": (_height > 190) | ((_height < 150) & (_code == "abc")),
        }
        _codes_with_height_categories = {
            "code_or_tall": ((_height < 150) & (_code == "abc")) | (_height > 190),
        }
        height_group = categorise(_height_with_codes_categories, default="na")
        height_group1 = categorise(_codes_with_height_categories, default="na")

    result = extract(Cohort, MockBackend, database)

    assert result == [
        dict(patient_id=1, height_group="tall_or_code", height_group1="code_or_tall"),
        dict(patient_id=2, height_group="tall_or_code", height_group1="code_or_tall"),
        dict(patient_id=3, height_group="tall_or_code", height_group1="code_or_tall"),
        dict(patient_id=4, height_group="na", height_group1="na"),
        dict(patient_id=5, height_group="na", height_group1="na"),
    ]


@pytest.mark.integration
def test_categorise_on_truthiness(database, setup_test_database):
    """Test truthiness of a Value from an exists aggregation"""
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
    ]
    setup_test_database(input_data)

    class Cohort:
        _code = table("clinical_events").filter(code="abc").exists()
        _codes_categories = {"yes": _code}
        abc = categorise(_codes_categories, default="na")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, abc="yes"),
        dict(patient_id=2, abc="na"),
        dict(patient_id=3, abc="yes"),
        dict(patient_id=4, abc="na"),
    ]


@pytest.mark.integration
def test_categorise_on_truthiness_from_filter(database, setup_test_database):
    """Test truthiness of a Value from a filtered value"""
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
        Events(PatientId=4, EventCode="def"),
    ]
    setup_test_database(input_data)

    class Cohort:
        _code = (
            table("clinical_events")
            .filter("code", is_in=["abc", "def"])
            .latest()
            .get("code")
        )
        _codes_categories = {"yes": _code}
        has_code = categorise(_codes_categories, default="na")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, has_code="yes"),
        dict(patient_id=2, has_code="na"),
        dict(patient_id=3, has_code="yes"),
        dict(patient_id=4, has_code="yes"),
    ]


@pytest.mark.integration
def test_categorise_multiple_truthiness_values(database, setup_test_database):
    """Test truthiness of a Value from a filtered value"""
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
        Events(PatientId=4, EventCode="def"),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True),
        PositiveTests(PatientId=2, PositiveResult=False),
        PositiveTests(PatientId=3, PositiveResult=False),
        PositiveTests(PatientId=4, PositiveResult=True),
    ]
    setup_test_database(input_data)

    class Cohort:
        _code = (
            table("clinical_events")
            .filter("code", is_in=["abc", "def"])
            .latest()
            .get("code")
        )
        _has_positive_test = table("positive_tests").filter(result=True).exists()
        _codes_categories = {"yes": _code & _has_positive_test}
        has_positive_code = categorise(_codes_categories, default="na")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, has_positive_code="yes"),
        dict(patient_id=2, has_positive_code="na"),
        dict(patient_id=3, has_positive_code="na"),
        dict(patient_id=4, has_positive_code="yes"),
    ]


@pytest.mark.integration
def test_categorise_invert(database, setup_test_database):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        RegistrationHistory(PatientId=5),
        Patients(PatientId=1, Height=194),  # tall with code - matches
        Patients(PatientId=2, Height=160.5),  # tall no code  - matches
        Patients(PatientId=3, Height=155.5),  # short with code - matches
        Patients(PatientId=4, Height=140.5),  # short no code
    ]
    setup_test_database(input_data)

    class Cohort:
        _height = table("patients").first_by("patient_id").get("height")
        _code = table("clinical_events").first_by("patient_id").get("code")

        # make sure the parentheses precedence is followed; these two expressions are equivalent
        _height_inverted = {
            "tall": _height > 190,
            "not_tall": ~(_height > 190),
        }
        height_group = categorise(_height_inverted, default="na")

    result = extract(Cohort, MockBackend, database)

    assert result == [
        dict(patient_id=1, height_group="tall"),
        dict(patient_id=2, height_group="not_tall"),
        dict(patient_id=3, height_group="not_tall"),
        dict(patient_id=4, height_group="not_tall"),
        dict(patient_id=5, height_group="na"),
    ]


@pytest.mark.integration
def test_categorise_invert_truthiness_values(database, setup_test_database):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
        Events(PatientId=4, EventCode="def"),
    ]
    setup_test_database(input_data)

    class Cohort:
        _code = (
            table("clinical_events")
            .filter("code", is_in=["abc", "def"])
            .latest()
            .get("code")
        )
        _codes_categories = {"yes": _code, "no": ~_code}
        has_code = categorise(_codes_categories, default="na")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, has_code="yes"),
        dict(patient_id=2, has_code="no"),
        dict(patient_id=3, has_code="yes"),
        dict(patient_id=4, has_code="yes"),
    ]


@pytest.mark.integration
def test_categorise_invert_combined_values(database, setup_test_database):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
        Events(PatientId=4, EventCode="def"),
        # Patient test results with dates
        PositiveTests(PatientId=1, PositiveResult=True),
        PositiveTests(PatientId=2, PositiveResult=False),
        PositiveTests(PatientId=3, PositiveResult=False),
        PositiveTests(PatientId=4, PositiveResult=True),
    ]
    setup_test_database(input_data)

    class Cohort:
        _code = (
            table("clinical_events")
            .filter("code", is_in=["abc", "def"])
            .latest()
            .get("code")
        )
        _has_positive_test = table("positive_tests").filter(result=True).exists()
        _codes_categories = {"neg_or_no_code": ~(_code & _has_positive_test)}
        result_group = categorise(_codes_categories, default="pos")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, result_group="pos"),
        dict(patient_id=2, result_group="neg_or_no_code"),
        dict(patient_id=3, result_group="neg_or_no_code"),
        dict(patient_id=4, result_group="pos"),
    ]


@pytest.mark.integration
def test_categorise_double_invert(database, setup_test_database):
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="abc"),
        Events(PatientId=4, EventCode="def"),
    ]
    setup_test_database(input_data)

    class Cohort:
        _code = (
            table("clinical_events")
            .filter("code", is_in=["abc", "def"])
            .latest()
            .get("code")
        )
        _codes_categories = {"yes": ~~_code}
        has_code = categorise(_codes_categories, default="na")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, has_code="yes"),
        dict(patient_id=2, has_code="na"),
        dict(patient_id=3, has_code="yes"),
        dict(patient_id=4, has_code="yes"),
    ]


@pytest.mark.integration
def test_categorise_multiple_truthiness_categories(database, setup_test_database):
    """
    Test categorisation on multiple truthy values
    This tests for a previous bug in sorting the reference nodes in category definitions.
    A truthy categorisation ({`x`: _codes}) creates a Comparator instance with a ValueFromRow
    as its LHS and tests for not-equal to None. In the query engine, we find all reference
    nodes from category definitions and sort them to ensure a consistent order (largely for
    tests) using the node column and source as a sort key,  The reference node for a
    ValueFromRow is a Row, which can't be sorted.  THis test checks the workaround for
    this scenario.
    """
    input_data = [
        RegistrationHistory(PatientId=1),
        RegistrationHistory(PatientId=2),
        RegistrationHistory(PatientId=3),
        RegistrationHistory(PatientId=4),
        RegistrationHistory(PatientId=5),
        Events(PatientId=1, EventCode="abc"),
        Events(PatientId=2, EventCode="xyz"),
        Events(PatientId=3, EventCode="uvw"),
        Events(PatientId=4, EventCode="def"),
        Events(PatientId=2, EventCode="lmn"),
    ]
    setup_test_database(input_data)

    class Cohort:
        _codes_1 = (
            table("clinical_events")
            .filter("code", is_in=["abc", "def"])
            .latest()
            .get("code")
        )
        _codes_2 = (
            table("clinical_events")
            .filter("code", is_in=["uvw", "xyz"])
            .latest()
            .get("code")
        )
        _codes_categories = {"1": _codes_1, "2": _codes_2}
        has_positive_code = categorise(_codes_categories, default="na")

    result = extract(Cohort, MockBackend, database)
    assert result == [
        dict(patient_id=1, has_positive_code="1"),
        dict(patient_id=2, has_positive_code="2"),
        dict(patient_id=3, has_positive_code="2"),
        dict(patient_id=4, has_positive_code="1"),
        dict(patient_id=5, has_positive_code="na"),
    ]


@pytest.mark.integration
def test_age_as_of(database, setup_test_database):
    input_data = [
        # Patient 1
        Patients(PatientId=1, DateOfBirth="1990-8-10"),
        RegistrationHistory(PatientId=1),
        Events(PatientId=1, Date="2020-10-01"),
        # Patient 2
        Patients(PatientId=2, DateOfBirth="2000-03-20"),
        RegistrationHistory(PatientId=2),
        Events(PatientId=2, Date="2018-02-01"),
    ]
    setup_test_database(input_data)

    class Cohort:
        age_in_2010 = table("patients").age_as_of("2010-06-01")
        age_at_last_event = table("patients").age_as_of(
            table("clinical_events").latest().get("date")
        )

    result = extract(Cohort, MockBackend, database)
    assert result == [
        {"patient_id": 1, "age_in_2010": 19, "age_at_last_event": 30},
        {"patient_id": 2, "age_in_2010": 10, "age_at_last_event": 17},
    ]


@mark_xfail_in_playback_mode
@pytest.mark.integration
def test_fetching_results_using_temporary_database(database, setup_test_database):
    setup_test_database(
        [
            *patient(1, event("abc", "2020-01-01")),
            *patient(2, event("xyz", "2020-01-01")),
        ]
    )

    class Cohort:
        code = table("clinical_events").latest().get("code")

    assert extract(Cohort, MockBackend, database, temporary_database="temp_tables") == [
        dict(patient_id=1, code="abc"),
        dict(patient_id=2, code="xyz"),
    ]
