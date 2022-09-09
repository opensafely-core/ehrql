import datetime

import sqlalchemy.orm

from databuilder.codes import CTV3Code, ICD10Code, SNOMEDCTCode
from databuilder.orm_factory import orm_class_from_ql_table
from databuilder.tables import EventFrame, PatientFrame, Series, table

Base = sqlalchemy.orm.declarative_base()


@table
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)
    sex = Series(str)


Patient = orm_class_from_ql_table(Base, patients)


@table
class vaccinations(EventFrame):
    date = Series(datetime.date)
    target_disease = Series(str)
    product_name = Series(str)


Vaccination = orm_class_from_ql_table(Base, vaccinations)


@table
class practice_registrations(EventFrame):
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    practice_pseudo_id = Series(int)
    practice_stp = Series(str)
    practice_nuts1_region_name = Series(str)


PracticeRegistration = orm_class_from_ql_table(Base, practice_registrations)


@table
class ons_deaths(EventFrame):
    date = Series(datetime.date)
    # TODO: Revisit this when we have support for multi-valued fields
    cause_of_death_01 = Series(ICD10Code)
    cause_of_death_02 = Series(ICD10Code)
    cause_of_death_03 = Series(ICD10Code)
    cause_of_death_04 = Series(ICD10Code)
    cause_of_death_05 = Series(ICD10Code)
    cause_of_death_06 = Series(ICD10Code)
    cause_of_death_07 = Series(ICD10Code)
    cause_of_death_08 = Series(ICD10Code)
    cause_of_death_09 = Series(ICD10Code)
    cause_of_death_10 = Series(ICD10Code)
    cause_of_death_11 = Series(ICD10Code)
    cause_of_death_12 = Series(ICD10Code)
    cause_of_death_13 = Series(ICD10Code)
    cause_of_death_14 = Series(ICD10Code)
    cause_of_death_15 = Series(ICD10Code)


ONSDeath = orm_class_from_ql_table(Base, ons_deaths)


@table
class coded_events(EventFrame):
    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)
    ctv3_code = Series(CTV3Code)
    numeric_value = Series(float)


CodedEvent = orm_class_from_ql_table(Base, coded_events)


@table
class medications(EventFrame):
    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)


Medication = orm_class_from_ql_table(Base, medications)


@table
class addresses(EventFrame):
    address_id = Series(int)
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    address_type = Series(int)
    rural_urban_classification = Series(int)
    imd_rounded = Series(int)
    msoa_code = Series(str)
    # Is the address potentially a match for a care home? (Using TPP's algorithm)
    care_home_is_potential_match = Series(bool)
    # These two fields look like they should be a single boolean, but this is how
    # they're represented in the data
    care_home_requires_nursing = Series(bool)
    care_home_does_not_require_nursing = Series(bool)


Address = orm_class_from_ql_table(Base, addresses)


@table
class sgss_covid_all_tests(EventFrame):
    specimen_taken_date = Series(datetime.date)
    is_positive = Series(bool)


SGSSCovidAllTestsResult = orm_class_from_ql_table(Base, sgss_covid_all_tests)


@table
class occupation_on_covid_vaccine_record(EventFrame):
    is_healthcare_worker = Series(bool)


OccupationOnCovidVaccineRecord = orm_class_from_ql_table(
    Base, occupation_on_covid_vaccine_record
)


@table
class emergency_care_attendances(EventFrame):
    id = Series(int)  # noqa: A003
    arrival_date = Series(datetime.date)
    discharge_destination = Series(SNOMEDCTCode)
    # TODO: Revisit this when we have support for multi-valued fields
    diagnosis_01 = Series(SNOMEDCTCode)
    diagnosis_02 = Series(SNOMEDCTCode)
    diagnosis_03 = Series(SNOMEDCTCode)
    diagnosis_04 = Series(SNOMEDCTCode)
    diagnosis_05 = Series(SNOMEDCTCode)
    diagnosis_06 = Series(SNOMEDCTCode)
    diagnosis_07 = Series(SNOMEDCTCode)
    diagnosis_08 = Series(SNOMEDCTCode)
    diagnosis_09 = Series(SNOMEDCTCode)
    diagnosis_10 = Series(SNOMEDCTCode)
    diagnosis_11 = Series(SNOMEDCTCode)
    diagnosis_12 = Series(SNOMEDCTCode)
    diagnosis_13 = Series(SNOMEDCTCode)
    diagnosis_14 = Series(SNOMEDCTCode)
    diagnosis_15 = Series(SNOMEDCTCode)
    diagnosis_16 = Series(SNOMEDCTCode)
    diagnosis_17 = Series(SNOMEDCTCode)
    diagnosis_18 = Series(SNOMEDCTCode)
    diagnosis_19 = Series(SNOMEDCTCode)
    diagnosis_20 = Series(SNOMEDCTCode)
    diagnosis_21 = Series(SNOMEDCTCode)
    diagnosis_22 = Series(SNOMEDCTCode)
    diagnosis_23 = Series(SNOMEDCTCode)
    diagnosis_24 = Series(SNOMEDCTCode)


EmergencyCareAttendance = orm_class_from_ql_table(Base, emergency_care_attendances)


@table
class hospital_admissions(EventFrame):
    id = Series(int)  # noqa: A003
    admission_date = Series(datetime.date)
    discharge_date = Series(datetime.date)
    admission_method = Series(str)
    # TODO: Revisit this when we have support for multi-valued fields
    all_diagnoses = Series(str)
    patient_classification = Series(str)
    days_in_critical_care = Series(int)


HospitalAdmission = orm_class_from_ql_table(Base, hospital_admissions)
