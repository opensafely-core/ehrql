import datetime

from databuilder.codes import CTV3Code, DMDCode, ICD10Code, SNOMEDCTCode
from databuilder.contracts.universal import patients
from databuilder.tables import Constraint, EventFrame, PatientFrame, Series, table

__all__ = [
    "patients",
    "vaccinations",
    "practice_registrations",
    "ons_deaths",
    "clinical_events",
    "medications",
    "addresses",
    "sgss_covid_all_tests",
    "occupation_on_covid_vaccine_record",
    "emergency_care_attendances",
    "hospital_admissions",
    "appointments",
    "ons_cis",
    "isaric_raw",
]


@table
class vaccinations(EventFrame):
    vaccination_id = Series(int)
    date = Series(datetime.date)
    target_disease = Series(str)
    product_name = Series(str)


@table
class practice_registrations(EventFrame):
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    practice_pseudo_id = Series(int)
    practice_stp = Series(
        str,
        constraints=[Constraint.Regex("E540000[0-9]{2}")],
    )
    practice_nuts1_region_name = Series(
        str,
        constraints=[
            Constraint.Categorical(
                [
                    "East Midlands",
                    "East of England",
                    "London",
                    "North East",
                    "North West",
                    "South East",
                    "South West",
                    "West Midlands",
                    "Yorkshire and the Humber",
                ]
            ),
        ],
    )


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


@table
class clinical_events(EventFrame):
    date = Series(datetime.date)
    snomedct_code = Series(SNOMEDCTCode)
    ctv3_code = Series(CTV3Code)
    numeric_value = Series(float)


@table
class medications(EventFrame):
    date = Series(datetime.date)
    dmd_code = Series(DMDCode)
    multilex_code = Series(str)


@table
class addresses(EventFrame):
    address_id = Series(int)
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    address_type = Series(int)
    rural_urban_classification = Series(int)
    imd_rounded = Series(int)
    msoa_code = Series(
        str,
        constraints=[Constraint.Regex("E020[0-9]{5}")],
    )
    has_postcode = Series(bool)
    # Is the address potentially a match for a care home? (Using TPP's algorithm)
    care_home_is_potential_match = Series(bool)
    # These two fields look like they should be a single boolean, but this is how
    # they're represented in the data
    care_home_requires_nursing = Series(bool)
    care_home_does_not_require_nursing = Series(bool)


@table
class sgss_covid_all_tests(EventFrame):
    specimen_taken_date = Series(datetime.date)
    is_positive = Series(bool)


@table
class occupation_on_covid_vaccine_record(EventFrame):
    is_healthcare_worker = Series(bool)


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


@table
class appointments(EventFrame):
    booked_date = Series(datetime.date)
    start_date = Series(datetime.date)


@table
class household_memberships_2020(PatientFrame):
    """
    Inferred household membership as of 2020-02-01, as determined by TPP using an as yet
    undocumented algorithm
    """

    household_pseudo_id = Series(int)
    household_size = Series(int)


@table
class ons_cis(EventFrame):
    """
    ONS Covid Infection Survery
    """

    visit_date = Series(datetime.date)
    visit_num = Series(int)
    is_opted_out_of_nhs_data_share = Series(bool)
    last_linkage_dt = Series(datetime.date)


@table
class isaric_raw(EventFrame):
    """
    A subset of the ISARIC data.

    These columns are deliberately all taken as strings while in a preliminary phase.
    They will later change to more appropriate data types.

    Descriptions taken from:
    https://github.com/isaric4c/wiki/blob/d6b87d59a277cf2f6deedeb5e8c1a970dbb970a3/ISARIC/CCP_REDCap_ISARIC_data_dictionary_codebook.pdf
    """

    # Demographics
    age = Series(
        str,
        description="Age",
    )
    age_factor = Series(
        str,
        description="TODO",
    )
    calc_age = Series(
        str,
        description="Calculated age (comparing date of birth with date of enrolment). May be inaccurate if a date of February 29 is used.",
    )
    sex = Series(
        str,
        description="Sex at birth.",
    )
    ethnic = Series(
        str,
        description="Ethnic group.",
    )

    # Clinical
    corona_ieorres = Series(
        str,
        description="Suspected or proven infection with pathogen of public health interest.",
    )
    # Note the coriona spelling here (compared with corona_ieorres).
    # The difference exists both in the TPP ISARIC_New database table,
    # and the ISARIC data dictionary.
    coriona_ieorres2 = Series(
        str,
        description="Proven or high likelihood of infection with pathogen of public health interest.",
    )
    coriona_ieorres3 = Series(
        str,
        description="Proven infection with pathogen of public health interest.",
    )
    inflammatory_mss = Series(
        str,
        description="Adult or child who meets case definition for inflammatory multi-system syndrome (MIS-C/MIS-A).",
    )

    # Vaccination
    covid19_vaccine = Series(
        str,
        description="Has the patient received a Covid-19 vaccine (open label licenced product)?",
    )
    covid19_vaccined = Series(
        datetime.date,
        description="Date first vaccine given (Covid-19) if known.",
    )
    covid19_vaccined_nk = Series(
        str,
        description="First vaccine given (Covid-19) but date not known.",
    )

    # Admission
    hostdat = Series(
        datetime.date,
        description="Admission date at this facility.",
    )
    readm_cov19 = Series(
        str,
        description="Is the patient being readmitted with Covid-19?",
    )
    hooccur = Series(
        str,
        description="Transfer from other facility?",
    )
    hostdat_transfer = Series(
        datetime.date,
        description="Admission date at previous facility.",
    )
    hostdat_transfernk = Series(
        str,
        description="Admission date at previous facility not known.",
    )

    dsstdat = Series(datetime.date)
    cestdat = Series(datetime.date)
    dsstdtc = Series(datetime.date)
    covid19_vaccine2d = Series(datetime.date)
    covid19_vaccine3d = Series(datetime.date)
