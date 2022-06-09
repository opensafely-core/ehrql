import datetime

import sqlalchemy.orm

from databuilder.codes import CTV3Code, SNOMEDCTCode
from databuilder.query_language import build_event_table, build_patient_table

from ...lib.util import orm_class_from_table

Base = sqlalchemy.orm.declarative_base()


patients = build_patient_table(
    "patients",
    {
        "date_of_birth": datetime.date,
        "sex": str,
    },
)

Patient = orm_class_from_table(Base, patients)


vaccinations = build_event_table(
    "vaccinations",
    {
        "date": datetime.date,
        "target_disease": str,
        "product_name": str,
    },
)

Vaccination = orm_class_from_table(Base, vaccinations)


practice_registrations = build_event_table(
    "practice_registrations",
    {
        "start_date": datetime.date,
        "end_date": datetime.date,
        "practice_pseudo_id": int,
    },
)

PracticeRegistration = orm_class_from_table(Base, practice_registrations)


ons_deaths = build_event_table(
    "ons_deaths",
    {
        "date": datetime.date,
    },
)

ONSDeath = orm_class_from_table(Base, ons_deaths)


coded_events = build_event_table(
    "coded_events",
    {
        "date": datetime.date,
        "snomedct_code": SNOMEDCTCode,
        "ctv3_code": CTV3Code,
        "numeric_value": float,
    },
)

CodedEvent = orm_class_from_table(Base, coded_events)


medications = build_event_table(
    "medications",
    {
        "date": datetime.date,
        "snomedct_code": SNOMEDCTCode,
    },
)

Medication = orm_class_from_table(Base, medications)
