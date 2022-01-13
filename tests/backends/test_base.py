from databuilder.backends.base import BaseBackend, Column, MappedTable
from databuilder.query_engines.base_sql import BaseSQLQueryEngine


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

    assert set(BasicBackend.tables) == {
        "patients",
        "clinical_events",
    }


def test_validate_all_backends():
    """
    Loops through all the backends, excluding test ones,
    and validates they meet any contract that they claim to
    """
    backends = [
        backend
        for backend in BaseBackend.__subclasses__()
        if backend.__module__.startswith("databuilder.backends.")
    ]

    for backend in backends:
        backend.validate_contracts()

    # Checks at least 3 backends
    assert len(backends) >= 3
