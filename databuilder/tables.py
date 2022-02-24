from databuilder.query_language import (
    DateSeries,
    IdSeries,
    StrSeries,
    build_patient_table,
)

from .contracts import universal

patients = build_patient_table(
    "patients",
    {
        "patient_id": IdSeries,
        "date_of_birth": DateSeries,
        "date_of_death": DateSeries,
        "sex": StrSeries,
    },
    contract=universal.Patients,
)
