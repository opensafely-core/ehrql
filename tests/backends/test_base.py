from cohortextractor.backends.base import BaseBackend, Column, MappedTable
from cohortextractor.query_engines.base_sql import BaseSQLQueryEngine


def test_backend_tables():
    """Test that a backend registers its table names"""

    class BasicBackend(BaseBackend):
        backend_id = "basic_test_backend"
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"

        patients = MappedTable(
            source="Patient",
            columns=dict(
                date_of_birth=Column("date", source="DateOfBirth"),
            ),
        )

        clinical_events = MappedTable(
            source="coded_events",
            columns=dict(
                code=Column("code", source="EventCode"),
                date=Column("date", source="Date"),
            ),
        )

    assert BasicBackend.tables == {
        "patients",
        "clinical_events",
    }
