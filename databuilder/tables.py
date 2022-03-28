from databuilder.query_language import (
    CodeSeries,
    DateSeries,
    FloatSeries,
    IdSeries,
    StrSeries,
    build_event_table,
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

events = build_event_table(
    "events",
    {
        "patient_id": IdSeries,
        "date": DateSeries,
        "code": CodeSeries,
        "value": FloatSeries,
    },
)

ons_deaths = build_patient_table(
    "ons_deaths",
    {
        "patient_id": IdSeries,
        "date_of_death": DateSeries,
    },
)
