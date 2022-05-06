from databuilder.query_language import DateSeries, StrSeries, build_patient_table

from .contracts import universal

patients = build_patient_table(
    "patients",
    {
        "date_of_birth": DateSeries,
        "date_of_death": DateSeries,
        "sex": StrSeries,
    },
    contract=universal.Patients,
)
