from cohortextractor.backends.base import BaseBackend, Column, MappedTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


class GraphnetBackend(BaseBackend):
    backend_id = "graphnet"
    query_engine_class = MssqlQueryEngine
    patient_join_column = "patient_id"

    patients = MappedTable(
        source="Patients",
        columns=dict(
            date_of_birth=Column("date", source="date_of_birth"),
        ),
    )
