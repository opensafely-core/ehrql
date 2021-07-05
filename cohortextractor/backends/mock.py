from ..query_engines.mssql import MssqlQueryEngine
from .base import BaseBackend, Column, SQLTable


class MockBackend(BaseBackend):
    """
    Mock backend for use in tests.
    """

    backend_id = "mock"
    query_engine_class = MssqlQueryEngine

    practice_registrations = SQLTable(
        source="practice_registrations",
        columns=dict(patient_id=Column("int", source="PatientId")),
    )
    clinical_events = SQLTable(
        source="events",
        columns=dict(
            code=Column("varchar", source="EventCode"),
            date=Column("varchar", source="Date"),
        ),
    )
