import json
from pathlib import Path

from databuilder.ehrql import Dataset, case, days, when
from databuilder.tables.beta import tpp as schema
from variables_lib import (
    address_as_of,
    age_as_of,
    create_sequential_variables,
    date_deregistered_from_all_supported_practices,
    emergency_care_diagnosis_matches,
    has_a_continuous_practice_registration_spanning,
    hospitalisation_diagnosis_matches,
    most_recent_bmi,
    practice_registration_as_of,
)

import codelists

dataset = Dataset()


#######################################################################################
# Import study dates defined in "./lib/design/study-dates.R" script and then exported
# to JSON
#######################################################################################
study_dates = json.loads(
    Path(__file__).parent.joinpath("study-dates.json").read_text(),
)

# Change these in design.R if necessary
firstpossiblevax_date = study_dates["firstpossiblevax_date"]
studystart_date = study_dates["studystart_date"]
studyend_date = study_dates["studyend_date"]
followupend_date = study_dates["followupend_date"]
firstpfizer_date = study_dates["firstpfizer_date"]
firstaz_date = study_dates["firstaz_date"]
firstmoderna_date = study_dates["firstmoderna_date"]


#######################################################################################
# Covid vaccine dates
#######################################################################################

# The old study def used 1900 as a minimum date so we replicate that here; but I think
# it only did this because it had to supply _some_ minimum date, which we don't need to
# here, so maybe we can drop this.
vax = schema.vaccinations.where(schema.vaccinations.date.is_after("1900-01-01"))

# Pfizer
create_sequential_variables(
    dataset,
    "covid_vax_pfizer_{n}_date",
    num_variables=4,
    events=vax.where(
        vax.product_name
        == "COVID-19 mRNA Vaccine Comirnaty 30micrograms/0.3ml dose conc for susp for inj MDV (Pfizer)"
    ),
    column="date",
)

# AZ
create_sequential_variables(
    dataset,
    "covid_vax_az_{n}_date",
    num_variables=4,
    events=vax.where(
        vax.product_name
        == "COVID-19 Vaccine Vaxzevria 0.5ml inj multidose vials (AstraZeneca)"
    ),
    column="date",
)

# Moderna
create_sequential_variables(
    dataset,
    "covid_vax_moderna_{n}_date",
    num_variables=4,
    events=vax.where(
        vax.product_name
        == "COVID-19 mRNA Vaccine Spikevax (nucleoside modified) 0.1mg/0.5mL dose disp for inj MDV (Moderna)"
    ),
    column="date",
)

# Any covid vaccine
create_sequential_variables(
    dataset,
    "covid_vax_disease_{n}_date",
    num_variables=4,
    events=vax.where(vax.target_disease == "SARS-2 CORONAVIRUS"),
    column="date",
)


#######################################################################################
# Aliases and common functions
#######################################################################################

boosted_date = dataset.covid_vax_disease_3_date
# We define baseline variables on the day _before_ the study date (start date = day of
# first possible booster vaccination)
baseline_date = boosted_date - days(1)

events = schema.clinical_events
meds = schema.medications
prior_events = events.where(events.date.is_on_or_before(baseline_date))
prior_meds = meds.where(meds.date.is_on_or_before(baseline_date))


def has_prior_event(codelist, where=True):
    return (
        prior_events.where(where)
        .where(prior_events.snomedct_code.is_in(codelist))
        .exists_for_patient()
    )


def last_prior_event(codelist, where=True):
    return (
        prior_events.where(where)
        .where(prior_events.snomedct_code.is_in(codelist))
        .sort_by(events.date)
        .last_for_patient()
    )


def has_prior_meds(codelist, where=True):
    return (
        prior_meds.where(where)
        .where(prior_meds.dmd_code.is_in(codelist))
        .exists_for_patient()
    )


#######################################################################################
# Admin and demographics
#######################################################################################

dataset.has_follow_up_previous_6weeks = has_a_continuous_practice_registration_spanning(
    start_date=boosted_date - days(6 * 7),
    end_date=boosted_date,
)

dataset.dereg_date = date_deregistered_from_all_supported_practices()

dataset.age = age_as_of(baseline_date)
# For JCVI group definitions
dataset.age_august2021 = age_as_of("2020-08-31")

dataset.sex = schema.patients.sex

# BMI
# https://github.com/opensafely/risk-factors-research/issues/51
bmi_measurement = most_recent_bmi(
    # This isn't _exactly_ 5 years as the old study used, but I can't see that would
    # matter here
    where=events.date.is_after(baseline_date - days(5 * 365)),
    minimum_age_at_measurement=16,
)
bmi_value = bmi_measurement.numeric_value

dataset.bmi = case(
    when((bmi_value >= 30.0) & (bmi_value < 35.0)).then("Obese I (30-34.9)"),
    when((bmi_value >= 35.0) & (bmi_value < 40.0)).then("Obese II (35-39.9)"),
    # Set maximum to avoid any impossibly extreme values being classified as obese
    when((bmi_value >= 40.0) & (bmi_value < 100.0)).then("Obese III (40+)"),
    default="Not obese",
)

# Ethnicity in 6 categories
dataset.ethnicity = (
    events.where(events.ctv3_code.is_in(codelists.ethnicity))
    .sort_by(events.date)
    .last_for_patient()
    .ctv3_code.to_category(codelists.ethnicity)
)

# I haven't translated the `with_ethnicity_from_sus` query below because all the logic
# for this would currently have to live in a QueryTable SQL definition rather than in
# ehrQL, making the ehrQL side of things trivial. The SQL is here:
# https://github.com/opensafely-core/cohort-extractor/blob/45967211/cohortextractor/tpp_backend.py#L2771-L2807
#
# If we were going to represent this logic in ehrQL we'd need some kind of UNION
# operator, and a `most_common_for_patient()` aggregation. We may well want both of
# those eventuallly, but not right now.
#
#    # ethnicity variable that takes data from SUS
#    ethnicity_6_sus = patients.with_ethnicity_from_sus(
#      returning="group_6",
#      use_most_frequent_code=True,
#      return_expectations={
#        "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
#        "incidence": 0.8,
#      },
#    ),


#######################################################################################
# Practice and patient ID variables
#######################################################################################

practice_reg = practice_registration_as_of(baseline_date)

dataset.practice_id = practice_reg.practice_pseudo_id
# STP is an NHS administration region based on geography
dataset.stp = practice_reg.practice_stp
# NHS administrative region
dataset.region = practice_reg.practice_nuts1_region_name

address = address_as_of(baseline_date)

# Middle Super Output Area
dataset.msoa = address.msoa_code
# Rurality
dataset.rural_urban = address.rural_urban_classification

# Index of Multiple Deprevation Rank (rounded down to nearest 100)
dataset.imd = address.imd_rounded

imd = dataset.imd
dataset.imd_Q5 = case(
    when((imd >= 0) & (imd < 32844 * 1 // 5)).then("1 (most deprived)"),
    when((imd >= 32844 * 1 // 5) & (imd < 32844 * 2 // 5)).then("2"),
    when((imd >= 32844 * 2 // 5) & (imd < 32844 * 3 // 5)).then("3"),
    when((imd >= 32844 * 3 // 5) & (imd < 32844 * 4 // 5)).then("4"),
    when((imd >= 32844 * 4 // 5) & (imd <= 32844)).then("5 (least deprived)"),
    default="Unknown",
)


#######################################################################################
# Occupation / residency
#######################################################################################

# Health or social care worker
vaxx_job = schema.occupation_on_covid_vaccine_record
dataset.hscworker = vaxx_job.where(vaxx_job.is_healthcare_worker).exists_for_patient()

# TPP care home flag
dataset.care_home_tpp = address.care_home_is_potential_match.if_null_then(False)

# Patients in long-stay nursing and residential care
dataset.care_home_code = has_prior_event(codelists.carehome)


#######################################################################################
# Pre-baseline events where event date is of interest
#######################################################################################

primary_care_covid_events = events.where(
    events.ctv3_code.is_in(
        codelists.covid_primary_care_code
        + codelists.covid_primary_care_positive_test
        + codelists.covid_primary_care_sequelae
    )
)

dataset.primary_care_covid_case_0_date = (
    primary_care_covid_events.where(events.date.is_on_or_before(baseline_date))
    .sort_by(events.date)
    .last_for_patient()
    .date
)

# Covid test dates from SGSS
covid_tests = schema.sgss_covid_all_tests
prior_tests = covid_tests.where(
    covid_tests.specimen_taken_date.is_on_or_before(baseline_date)
)
dataset.covid_test_0_date = prior_tests.specimen_taken_date.maximum_for_patient()
dataset.postest_0_date = prior_tests.where(
    prior_tests.is_positive
).specimen_taken_date.maximum_for_patient()


# Emergency attendance for covid
emerg_care = schema.emergency_care_attendances

dataset.covidemergency_0_date = (
    emergency_care_diagnosis_matches(emerg_care, codelists.covid_emergency)
    .where(emerg_care.arrival_date.is_on_or_before(baseline_date))
    .sort_by(emerg_care.arrival_date)
    .last_for_patient()
    .arrival_date
)


# Positive covid admission prior to study start date
hosp = schema.hospital_admissions

dataset.covidadmitted_0_date = (
    hospitalisation_diagnosis_matches(hosp, codelists.covid_icd10)
    .where(hosp.admission_date.is_on_or_before(baseline_date))
    .where(
        hosp.admission_method.is_in(
            ["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]
        )
    )
    .sort_by(hosp.admission_date)
    .last_for_patient()
    .admission_date
)


#######################################################################################
# Clinical information as at (day before) 3rd / booster dose date
#######################################################################################

# From PRIMIS

# Asthma Admission codes
astadm = has_prior_event(codelists.astadm)
# Asthma Diagnosis code
ast = has_prior_event(codelists.ast)

# Asthma systemic steroid prescription code in month 1
astrxm1 = has_prior_meds(
    codelists.astrx,
    where=meds.date.is_after(baseline_date - days(30)),
)
# Asthma systemic steroid prescription code in month 2
astrxm2 = has_prior_meds(
    codelists.astrx,
    where=(
        meds.date.is_after(baseline_date - days(60))
        & meds.date.is_on_or_before(baseline_date - days(30))
    ),
)
# Asthma systemic steroid prescription code in month 3
astrxm3 = has_prior_meds(
    codelists.astrx,
    where=(
        meds.date.is_after(baseline_date - days(90))
        & meds.date.is_on_or_before(baseline_date - days(60))
    ),
)
dataset.asthma = astadm | (ast & astrxm1 & astrxm2 & astrxm3)

# Chronic Neurological Disease including Significant Learning Disorder
dataset.chronic_neuro_disease = has_prior_event(codelists.cns_cov)

# Chronic Respiratory Disease
resp_cov = has_prior_event(codelists.resp_cov)
dataset.chronic_resp_disease = dataset.asthma | resp_cov

# Severe Obesity
bmi_stage_event = last_prior_event(codelists.bmi_stage)
sev_obesity_event = last_prior_event(
    codelists.sev_obesity,
    where=((events.date >= bmi_stage_event.date) & (events.numeric_value != 0.0)),
)
bmi_event = last_prior_event(codelists.bmi, where=(events.numeric_value != 0.0))

dataset.sev_obesity = (sev_obesity_event.date > bmi_event.date) | (
    bmi_event.numeric_value >= 40.0
)

# Diabetes
diab_date = last_prior_event(codelists.diab).date
dmres_date = last_prior_event(codelists.dmres).date

dataset.diabetes = (dmres_date < diab_date) | (
    diab_date.is_not_null() & dmres_date.is_null()
)

# Severe Mental Illness codes
sev_mental_date = last_prior_event(codelists.sev_mental).date
# Remission codes relating to Severe Mental Illness
smhres_date = last_prior_event(codelists.smhres).date

dataset.sev_mental = (smhres_date < sev_mental_date) | (
    sev_mental_date.is_not_null() & smhres_date.is_null()
)

# Chronic heart disease codes
dataset.chronic_heart_disease = has_prior_event(codelists.chd_cov)

# Chronic kidney disease diagnostic codes
ckd = has_prior_event(codelists.ckd_cov)

# Chronic kidney disease codes - all stages
ckd15_date = last_prior_event(codelists.ckd15).date
# Chronic kidney disease codes-stages 3 - 5
ckd35_date = last_prior_event(codelists.ckd35).date

dataset.chronic_kidney_disease = ckd | (ckd35_date >= ckd15_date)

# Chronic Liver disease codes
dataset.chronic_liver_disease = has_prior_event(codelists.cld)

# Immunosuppression diagnosis codes
immdx = has_prior_event(codelists.immdx_cov)

# Immunosuppression medication codes
immrx = has_prior_meds(
    codelists.immrx,
    where=(meds.date.is_after(baseline_date - days(182))),
)

dataset.immunosuppressed = immrx | immdx

# Asplenia or Dysfunction of the Spleen codes
dataset.asplenia = has_prior_event(codelists.spln_cov)

# Wider Learning Disability
dataset.learndis = has_prior_event(codelists.learndis)

# To represent household contact of shielding individual
dataset.hhld_imdef_dat = last_prior_event(codelists.hhld_imdef).date


# This section is commented out in the original study so leaving commented out here

#    # #####################################
#    # # primis employment codelists
#    # #####################################
#    #
#    # # Carer codes
#    # carer_date=patients.with_these_clinical_events(
#    #   codelists.carer,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # No longer a carer codes
#    # notcarer_date=patients.with_these_clinical_events(
#    #   codelists.notcarer,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # Employed by Care Home codes
#    # carehome_date=patients.with_these_clinical_events(
#    #   codelists.carehomeemployee,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # Employed by nursing home codes
#    # nursehome_date=patients.with_these_clinical_events(
#    #   codelists.nursehomeemployee,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # Employed by domiciliary care provider codes
#    # domcare_date=patients.with_these_clinical_events(
#    #   codelists.domcareemployee,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),


dataset.cancer = has_prior_event(
    codelists.cancer_nonhaem_snomed + codelists.cancer_haem_snomed,
    where=events.date.is_after(baseline_date - days(int(3 * 365.25))),
)


#######################################################################################
# JCVI groups
#######################################################################################

# Shielding - Clinically Extremely Vulnerable
#
# The shielded patient list was retired in March/April 2021 when shielding ended
# so it might be worth using that as the end date instead of index_date, as we're not sure
# what has happened to these codes since then, e.g. have doctors still been adding new
# shielding flags or low-risk flags? Depends what you're looking for really. Could investigate separately.
# Ever coded as Clinically Extremely Vulnerable
date_severely_clinically_vulnerable = last_prior_event(codelists.shield).date
dataset.cev_ever = date_severely_clinically_vulnerable.is_not_null()

# NOT SHIELDED GROUP (medium and low risk) - only flag if later than 'shielded'
less_vulnerable = has_prior_event(
    codelists.nonshield,
    where=events.date.is_after(date_severely_clinically_vulnerable),
)

dataset.cev = dataset.cev_ever & ~less_vulnerable

# End of life
endoflife_coding = has_prior_event(codelists.eol)
midazolam = has_prior_meds(codelists.midazolam)
dataset.endoflife = midazolam | endoflife_coding

# Housebound
housebound_date = last_prior_event(codelists.housebound).date
no_longer_housebound = has_prior_event(
    codelists.no_longer_housebound,
    where=events.date.is_on_or_after(housebound_date),
)
moved_into_care_home = has_prior_event(
    codelists.carehome,
    where=events.date.is_on_or_after(housebound_date),
)

dataset.housebound = (
    housebound_date.is_not_null() & ~no_longer_housebound & ~moved_into_care_home
)

dataset.prior_covid_test_frequency = prior_tests.where(
    prior_tests.specimen_taken_date.is_after(baseline_date - days(26 * 7))
).count_for_patient()

# Overnight hospital admission at time of 3rd / booster dose
dataset.inhospital = (
    hosp.where(hosp.admission_date.is_on_or_before(boosted_date))
    .where(hosp.discharge_date.is_on_or_after(boosted_date))
    .where(
        # See https://github.com/opensafely-core/cohort-extractor/pull/497 for codes
        # See https://docs.opensafely.org/study-def-variables/#sus for more info
        hosp.admission_method.is_in(
            [
                "11",
                "12",
                "13",
                "21",
                "2A",
                "22",
                "23",
                "24",
                "25",
                "2D",
                "28",
                "2B",
                "81",
            ]
        )
    )
    # Ordinary admissions only
    .where(hosp.patient_classification == "1")
    .exists_for_patient()
)


#######################################################################################
# Post-baseline variables (outcomes)
#######################################################################################

# Positive case identification after study start date
dataset.primary_care_covid_case_date = (
    primary_care_covid_events.where(events.date.is_on_or_after(boosted_date))
    .sort_by(events.date)
    .first_for_patient()
    .date
)

# Covid test dates from SGSS
post_baseline_tests = covid_tests.where(
    covid_tests.specimen_taken_date.is_on_or_after(boosted_date)
)
dataset.covid_tests_date = post_baseline_tests.specimen_taken_date.minimum_for_patient()
# Positive covid test
dataset.postest_date = post_baseline_tests.where(
    post_baseline_tests.is_positive
).specimen_taken_date.minimum_for_patient()


# Post baseline date emergency care attendance
def post_baseline_ec_date(diagnoses=None, where=True):
    return (
        (
            emergency_care_diagnosis_matches(emerg_care, diagnoses)
            if diagnoses
            else emerg_care
        )
        .where(emerg_care.arrival_date.is_on_or_after(boosted_date))
        .where(where)
        .sort_by(emerg_care.arrival_date)
        .first_for_patient()
        .arrival_date
    )


# Emergency attendance for covid, as per discharge diagnosis
dataset.covidemergency_date = post_baseline_ec_date(codelists.covid_emergency)

# Emergency attendance for covid, as per discharge diagnosis, resulting in discharge to
# hospital
dataset.covidemergencyhosp_date = post_baseline_ec_date(
    codelists.covid_emergency,
    where=emerg_care.discharge_destination.is_in(codelists.discharged_to_hospital),
)


#    # emergency attendance for respiratory illness
#    # FIXME -- need to define codelist
#    # respemergency_date=patients.attended_emergency_care(
#    #   returning="date_arrived",
#    #   date_format="YYYY-MM-DD",
#    #   on_or_after="covid_vax_disease_3_date",
#    #   with_these_diagnoses = codelists.resp_emergency,
#    #   find_first_match_in_period=True,
#    # ),
#
#    # emergency attendance for respiratory illness, resulting in discharge to hospital
#    # FIXME -- need to define codelist
#    # respemergencyhosp_date=patients.attended_emergency_care(
#    #   returning="date_arrived",
#    #   date_format="YYYY-MM-DD",
#    #   on_or_after="covid_vax_disease_3_date",
#    #   find_first_match_in_period=True,
#    #   with_these_diagnoses = codelists.resp_emergency,
#    #   discharged_to = codelists.discharged_to_hospital,
#    # ),


# Any emergency attendance
dataset.emergency_date = post_baseline_ec_date(diagnoses=None)

# Emergency attendance resulting in discharge to hospital
dataset.emergencyhosp_date = post_baseline_ec_date(
    diagnoses=None,
    where=emerg_care.discharge_destination.is_in(codelists.discharged_to_hospital),
)


# Post baseline date hosptial admission
def post_baseline_admission_date(codelist=None, where=True):
    return (
        (hospitalisation_diagnosis_matches(hosp, codelist) if codelist else hosp)
        .where(hosp.admission_date.is_on_or_after(boosted_date))
        # Ordinary admissions only
        .where(hosp.patient_classification == "1")
        .where(where)
        .sort_by(hosp.admission_date)
        .first_for_patient()
        .admission_date
    )


# Unplanned hospital admission
dataset.admitted_unplanned_date = post_baseline_admission_date(
    where=hosp.admission_method.is_in(
        ["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]
    )
)

# Planned hospital admission
dataset.admitted_planned_date = post_baseline_admission_date(
    where=hosp.admission_method.is_in(["11", "12", "13", "81"])
)

# Positive covid admission prior to study start date
dataset.covidadmitted_date = post_baseline_admission_date(
    codelist=codelists.covid_icd10,
    where=hosp.admission_method.is_in(
        ["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]
    ),
)

# Record dates of hospitalisation and days in critical care for the first three
# hospitalisations after study start
covid_admissions = (
    hospitalisation_diagnosis_matches(hosp, codelists.covid_icd10)
    .where(
        hosp.admission_method.is_in(
            ["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"]
        )
    )
    .where(hosp.admission_date.is_on_or_after(boosted_date))
)

create_sequential_variables(
    dataset,
    "potentialcovidcritcare_{n}_date",
    covid_admissions,
    num_variables=3,
    column="admission_date",
)

create_sequential_variables(
    dataset,
    "potentialcovidcritcare_{n}_ccdays",
    covid_admissions,
    num_variables=3,
    column="days_in_critical_care",
    sort_column="admission_date",
)


#######################################################################################
# Population
#######################################################################################

registered = practice_registration_as_of(baseline_date).exists_for_patient()

dataset.define_population(
    registered
    & (dataset.age_august2021 >= 18)
    & boosted_date.is_on_or_after(studystart_date)
    & boosted_date.is_on_or_before(studyend_date)
)
