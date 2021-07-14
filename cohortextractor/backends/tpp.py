from cohortextractor.backends.base import BaseBackend, Column, SQLTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


class TPPBackend(BaseBackend):
    backend_id = "tpp"
    query_engine_class = MssqlQueryEngine
    patient_join_column = "Patient_ID"

    clinical_events = SQLTable(
        source="CodedEvent",
        columns=dict(
            code=Column("varchar", source="CTV3Code"),
            date=Column("datetime", source="ConsultationDate"),
        ),
    )

    practice_registrations = SQLTable(
        source="RegistrationHistory",
    )
