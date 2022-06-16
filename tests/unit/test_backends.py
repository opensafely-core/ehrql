from databuilder.backends.base import BaseBackend, Column, MappedTable
from databuilder.query_engines.base_sql import BaseSQLQueryEngine


class TestBackend(BaseBackend):
    backend_id = "tests_unit_test_backends"
    query_engine_class = BaseSQLQueryEngine
    patient_join_column = "patient_id"

    patients = MappedTable(
        source="patients",
        columns=dict(
            date_of_birth=Column("date", source="DateOfBirth"),
        ),
    )
    practice_registrations = MappedTable(
        source="practice_registrations",
        columns=dict(
            date_start=Column("date", source="StartDate"),
            date_end=Column("date", source="EndDate"),
        ),
    )


def test_backend_tables():
    """Test that a backend registers its table names"""

    assert set(TestBackend.tables) == {
        "patients",
        "practice_registrations",
    }
