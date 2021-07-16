from cohortextractor.backends.base import BaseBackend, Column, MappedTable, QueryTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


class TPPBackend(BaseBackend):
    backend_id = "tpp"
    query_engine_class = MssqlQueryEngine
    patient_join_column = "Patient_ID"

    clinical_events = MappedTable(
        source="CodedEvent",
        columns=dict(
            code=Column("varchar", source="CTV3Code"),
            date=Column("datetime", source="ConsultationDate"),
        ),
    )

    practice_registrations = MappedTable(
        source="RegistrationHistory",
        columns=dict(
            date_start=Column("datetime", source="StartDate"),
            date_end=Column("datetime", source="EndDate"),
        ),
    )

    sgss_sars_cov_2 = QueryTable(
        columns=dict(
            date=Column("date"),
            positive_result=Column("boolean"),
        ),
        query="""
            SELECT Patient_ID as patient_id, Specimen_Date AS date, 1 AS positive_result FROM SGSS_AllTests_Positive
            UNION ALL
            SELECT Patient_ID as patient_id, Specimen_Date AS date, 0 AS positive_result FROM SGSS_AllTests_Negative
        """,
    )
