import datetime

import sqlalchemy.orm

from databuilder.codes import CTV3Code, ICD10Code, SNOMEDCTCode
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
        "practice_stp": str,
        "practice_nuts1_region_name": str,
    },
)

PracticeRegistration = orm_class_from_table(Base, practice_registrations)


ons_deaths = build_event_table(
    "ons_deaths",
    {
        "date": datetime.date,
        # TODO: Revisit this when we have support for multi-valued fields
        **{f"cause_of_death_{i:02d}": ICD10Code for i in range(1, 16)},
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


addresses = build_event_table(
    "addresses",
    {
        "address_id": int,
        "start_date": datetime.date,
        "end_date": datetime.date,
        "address_type": int,
        "rural_urban_classification": int,
        "imd_rounded": int,
        "msoa_code": str,
        # Is the address potentially a match for a care home? (Using TPP's algorithm)
        "care_home_is_potential_match": bool,
        # These two fields look like they should be a single boolean, but this is how
        # they're represented in the data
        "care_home_requires_nursing": bool,
        "care_home_does_not_require_nursing": bool,
    },
)

Address = orm_class_from_table(Base, addresses)


sgss_covid_all_tests = build_event_table(
    "sgss_covid_all_tests",
    {
        "specimen_taken_date": datetime.date,
        "is_positive": bool,
    },
)

SGSSCovidAllTestsResult = orm_class_from_table(Base, sgss_covid_all_tests)


occupation_on_covid_vaccine_record = build_event_table(
    "occupation_on_covid_vaccine_record",
    {
        "is_healthcare_worker": bool,
    },
)

OccupationOnCovidVaccineRecord = orm_class_from_table(
    Base, occupation_on_covid_vaccine_record
)


emergency_care_attendances = build_event_table(
    "emergency_care_attendances",
    {
        "id": int,
        "arrival_date": datetime.date,
        "discharge_destination": SNOMEDCTCode,
        # TODO: Revisit this when we have support for multi-valued fields
        **{f"diagnosis_{i:02d}": SNOMEDCTCode for i in range(1, 25)},
    },
)

EmergencyCareAttendance = orm_class_from_table(Base, emergency_care_attendances)


hospital_admissions = build_event_table(
    "hospital_admissions",
    {
        "id": int,
        "admission_date": datetime.date,
        "discharge_date": datetime.date,
        "admission_method": str,
        # TODO: Revisit this when we have support for multi-valued fields
        "all_diagnoses": str,
        "patient_classification": str,
        "days_in_critical_care": int,
    },
)

HospitalAdmission = orm_class_from_table(Base, hospital_admissions)
