import pytest

from cohortextractor.backends.base import BaseBackend, Column, SQLTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine
from cohortextractor.query_language import table
from cohortextractor.query_utils import get_column_definitions


class MockBackend(BaseBackend):
    practice_registrations = SQLTable(
        source="registrations",
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
        column_definitions=column_definitions, backend=MockBackend()
    )

    sql = query_engine.get_sql()
    assert (
        sql == "SELECT * INTO group_table_0 FROM (\n"
        "SELECT clinical_events.code, clinical_events.patient_id \n"
        "FROM (SELECT EventCode AS code, patient_id AS patient_id \n"
        "FROM events) AS clinical_events\n) t\n\n\n"
        "SELECT practice_registrations.patient_id AS patient_id, group_table_0.code "
        "AS output_value \nFROM practice_registrations LEFT OUTER JOIN group_table_0 "
        "ON practice_registrations.patient_id = group_table_0.patient_id"
    )


def test_invalid_table():
    class Cohort:
        output_value = table("unknown").get("code")

    column_definitions = get_column_definitions(Cohort)
    query_engine = MssqlQueryEngine(
        column_definitions=column_definitions, backend=MockBackend()
    )
    with pytest.raises(ValueError, match="Unknown table 'unknown'"):
        query_engine.get_sql()
