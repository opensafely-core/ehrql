from datetime import date, timedelta

from databuilder.ehrql import Dataset, case, when
from databuilder.tables.beta.tpp import (
    clinical_events,
    emergency_care_attendances,
    hospital_admissions,
    patients,
    practice_registrations,
    sgss_covid_all_tests,
    ons_deaths,
)

import codelists_ehrql
from variable_lib import (
    has_matching_event,
    address_as_of,
    age_as_of,
    emergency_care_diagnosis_matches,
    hospitalisation_diagnosis_matches,
    practice_registration_as_of,
)

# Define list of hospital admission methods
hospital_admission_methods = [
    "21",
    "22",
    "23",
    "24",
    "25",
    "2A",
    "2B",
    "2C",
    "2D",
    "28",
]

# COMBINE CODELISTS
# Containing primary care covid events
primary_care_covid_events = clinical_events.where(
    clinical_events.ctv3_code.is_in(
        codelists_ehrql.covid_primary_care_code
        + codelists_ehrql.covid_primary_care_positive_test
        + codelists_ehrql.covid_primary_care_sequelae
    )
)

# Set index date
# TODO this is just an example for testing, something like --index-date-range
# needs to be added https://github.com/opensafely-core/databuilder/issues/741
index_date = date(2022, 9, 25)

# Create dataset
dataset = Dataset()

###############################################################################
# Preprocessing data for later use
###############################################################################

address = address_as_of(index_date)
prior_events = clinical_events.where(clinical_events.date.is_on_or_before(index_date))
prior_tests = sgss_covid_all_tests.where(
    sgss_covid_all_tests.specimen_taken_date.is_on_or_before(index_date)
)

###############################################################################
# Define and extract demographic dataset variables
###############################################################################

# Demographic variables
dataset.sex = patients.sex
dataset.age = age_as_of(index_date)
dataset.has_died = ons_deaths.where(ons_deaths.date <= index_date).exists_for_patient()

# TPP care home flag
dataset.care_home_tpp = address.care_home_is_potential_match.if_null_then(False)

# Patients in long-stay nursing and residential care
dataset.care_home_code = has_matching_event(prior_events, codelists_ehrql.carehome)

# Middle Super Output Area (MSOA)
dataset.msoa = address.msoa_code

# Practice registration
practice_reg = practice_registration_as_of(index_date)
dataset.registered = practice_reg.exists_for_patient()

# STP is an NHS administration region based on geography
dataset.stp = practice_reg.practice_stp

# NHS administrative region
dataset.region = practice_reg.practice_nuts1_region_name

###############################################################################
# Define and extract SINGLE-DAY EVENTS
# Did any event occur on this day?
###############################################################################

# Positive COVID test
dataset.postest_01 = prior_tests.where(
    (prior_tests.specimen_taken_date == index_date) & (prior_tests.is_positive)
).exists_for_patient()

# Positive case identification
dataset.primary_care_covid_case_01 = primary_care_covid_events.where(
    (clinical_events.date == index_date)
).exists_for_patient()

# Emergency attendance for COVID
dataset.covidemergency_01 = (
    emergency_care_diagnosis_matches(
        emergency_care_attendances, codelists_ehrql.covid_emergency
    )
    .where(emergency_care_attendances.arrival_date == index_date)
    .exists_for_patient()
)

# COVID hospital admission
dataset.covidadmitted_01 = (
    hospitalisation_diagnosis_matches(hospital_admissions, codelists_ehrql.covid_icd10)
    .where(hospital_admissions.admission_date == index_date)
    .where(hospital_admissions.admission_method.is_in(hospital_admission_methods))
    .exists_for_patient()
)

# Composite single-day variable
dataset.any_infection_or_disease_01 = (
    dataset.postest_01
    | dataset.primary_care_covid_case_01
    | dataset.covidemergency_01
    | dataset.covidadmitted_01
)

###############################################################################
# Define and extract 14-DAY EVENTS
# Did any event occur within the last 14 days?
###############################################################################

# Positive COVID test
dataset.postest_14 = prior_tests.where(
    (prior_tests.specimen_taken_date >= (index_date - timedelta(days=13)))
    & (prior_tests.specimen_taken_date <= index_date)
    & (prior_tests.is_positive)
).exists_for_patient()

# Positive case identification
dataset.primary_care_covid_case_14 = primary_care_covid_events.where(
    (clinical_events.date >= (index_date - timedelta(days=13)))
    & (clinical_events.date <= index_date)
).exists_for_patient()

# Emergency attendance for COVID
dataset.covidemergency_14 = (
    emergency_care_diagnosis_matches(
        emergency_care_attendances, codelists_ehrql.covid_emergency
    )
    .where(
        (emergency_care_attendances.arrival_date >= (index_date - timedelta(days=13)))
        & (emergency_care_attendances.arrival_date <= index_date)
    )
    .exists_for_patient()
)

# COVID hospital admission
dataset.covidadmitted_14 = (
    hospitalisation_diagnosis_matches(hospital_admissions, codelists_ehrql.covid_icd10)
    .where(
        (hospital_admissions.admission_date >= (index_date - timedelta(days=13)))
        & (hospital_admissions.admission_date <= index_date)
    )
    .where(hospital_admissions.admission_method.is_in(hospital_admission_methods))
    .exists_for_patient()
)

# Composite 14-day variable
dataset.any_infection_or_disease_14 = (
    dataset.postest_14
    | dataset.primary_care_covid_case_14
    | dataset.covidemergency_14
    | dataset.covidadmitted_14
)

###############################################################################
# Define and extract EVER-DAY EVENTS
# Did any event occur any time up to and including this day?
###############################################################################

# Positive COVID test
dataset.postest_ever = prior_tests.where(
    (prior_tests.specimen_taken_date <= index_date) & (prior_tests.is_positive)
).exists_for_patient()

# Positive case identification
dataset.primary_care_covid_case_ever = primary_care_covid_events.where(
    (clinical_events.date <= index_date)
).exists_for_patient()

# Emergency attendance for COVID
dataset.covidemergency_ever = (
    emergency_care_diagnosis_matches(
        emergency_care_attendances, codelists_ehrql.covid_emergency
    )
    .where((emergency_care_attendances.arrival_date <= index_date))
    .exists_for_patient()
)

# COVID hospital admission
dataset.covidadmitted_ever = (
    hospitalisation_diagnosis_matches(hospital_admissions, codelists_ehrql.covid_icd10)
    .where((hospital_admissions.admission_date <= index_date))
    .where(hospital_admissions.admission_method.is_in(hospital_admission_methods))
    .exists_for_patient()
)

# Composite "ever" variable
dataset.any_infection_or_disease_ever = (
    dataset.postest_ever
    | dataset.primary_care_covid_case_ever
    | dataset.covidemergency_ever
    | dataset.covidadmitted_ever
)

###############################################################################
# Define dataset restrictions
###############################################################################

has_practice_reg = practice_reg.exists_for_patient()
has_msoa_not_null = dataset.msoa.is_not_null()
has_sex_f_or_m = dataset.sex.is_in(["female", "male"])
has_age_between_2_and_120 = (dataset.age >= 2) & (dataset.age <= 120)
has_not_died = ~dataset.has_died
has_no_care_home_status = ~(dataset.care_home_tpp | dataset.care_home_code)

###############################################################################
# Apply dataset restrictions and define study population
###############################################################################

dataset.define_population(
    has_practice_reg
    & has_sex_f_or_m
    & has_age_between_2_and_120
    & has_not_died
    & has_no_care_home_status
    & has_msoa_not_null
)
