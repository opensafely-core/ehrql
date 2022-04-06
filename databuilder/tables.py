from asyncio import events

from databuilder.query_language import (
    DateSeries,
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

registrations = build_event_table(
    "registrations",
    {
        "patient_id": IdSeries,
        "date_from": DateSeries,
        "date_to": DateSeries,
        "practice_id": IdSeries,
        "stp": StrSeries,
    }
)

events = build_event_table(
    "events",
    {
        "patient_id": IdSeries,
        "date": DateSeries,
        "code": StrSeries,
    }
)
