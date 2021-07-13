from cohortextractor.backends.base import BaseBackend, Column, SQLTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


class TPPBackend(BaseBackend):
    backend_id = "tpp"
    query_engine_class = MssqlQueryEngine

    clinical_events = SQLTable(
        source="CodedEvent",
        columns=dict(
            code=Column("varchar", source="CTV3Code"),
            patient_id=Column("int", source="Patient_ID"),
        ),
    )

    practice_registrations = SQLTable(
        source="RegistrationHistory",
        columns=dict(
            patient_id=Column("int", source="Patient_ID"),
        ),
    )
