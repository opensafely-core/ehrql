import datetime

from databuilder.query_language import build_patient_table

from .contracts import universal

patients = build_patient_table(
    "patients",
    {
        "date_of_birth": datetime.date,
        "date_of_death": datetime.date,
        "sex": str,
    },
    contract=universal.Patients,
)
