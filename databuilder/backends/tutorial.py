import databuilder.tables.beta.tutorial
from databuilder.query_engines.csv import CSVQueryEngine

from .base import BaseBackend, MappedTable


class TutorialBackend(BaseBackend):
    """Backend for working with tutorial data."""

    query_engine_class = CSVQueryEngine
    patient_join_column = "patient_id"
    implements = [databuilder.tables.beta.tutorial]

    patient_demographics = MappedTable(
        source="patient_demographics",
        columns=dict(
            patient_id="patient_id",
            sex="sex",
            date_of_birth="date_of_birth",
            date_of_death="date_of_death",
        ),
    )

    prescriptions = MappedTable(
        source="prescriptions",
        columns=dict(
            patient_id="patient_id",
            prescribed_dmd_code="prescribed_dmd_code",
            processing_date="processing_date",
        ),
    )
