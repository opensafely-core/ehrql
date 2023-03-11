# where EHRQl is defined. Only really need Dastaset, tehe others are specific
from databuilder.ehrql import days, case, when
# this is where we import the schema to run the study with
from databuilder.tables.beta.tpp import (
  patients,
  practice_registrations,
  clinical_events,
  vaccinations,
  sgss_covid_all_tests,
  hospital_admissions
)
import datetime

from variable_lib import (
  age_as_of,
  has_died,
  address_as_of,
  create_sequential_variables,
  hospitalisation_diagnosis_matches
)
import codelists

study_start_date = datetime.date(2020, 11, 1)
study_end_date = datetime.date(2023, 1, 31)

minimum_registration = 90  # ~3 months of previous registration
covid_to_longcovid_lag = 84  # 12 weeks
vaccine_effective_lag = 14  # 2 weeks for vaccine to become effective
vaccine_to_longcovid_lag = covid_to_longcovid_lag + vaccine_effective_lag


def add_common_variables(dataset, study_start_date, end_date, population):
    # practice registration selection
    registrations = practice_registrations \
        .where(practice_registrations.start_date <= study_start_date - days(minimum_registration)) \
        .except_where(practice_registrations.end_date <= study_start_date)
# 08/02 - because we are using .except_where instaed of .where we are not dropping people with NULL start date
# it is possible that null start date is a data quality problem.
# So to keep consistent with other devs and cohort_extractor. Switch to a .where and therefore drop null start daters

    # get the number of registrations in this period to exclude anyone with >1 in the `set_population` later
    registrations_number = registrations.count_for_patient()

    # need to get the start and end date of last registration only
    registration = registrations \
        .sort_by(practice_registrations.start_date).last_for_patient()

    # need to find out if they had a hospitalisation for covid and censor then
    # note (18/01): needs looking at before I can use it.
    # hospitalised = hospital_admissions.where(hospital_admissions.all_diagnoses.contains(codelists.covidhosp))
    # then add into the end_date definition below (or as a secondary end date for sensitivity analysis?)

    dataset.pt_start_date = case(
        when(registration.start_date + days(minimum_registration) > study_start_date).then(registration.start_date + days(minimum_registration)),
        default=study_start_date,
    )

    dataset.pt_end_date = case(
        when(registration.end_date.is_null()).then(end_date),
        when(registration.end_date > end_date).then(end_date),
        default=registration.end_date,
    )

    # Demographic variables
    dataset.sex = patients.sex
    dataset.age = age_as_of(study_start_date)
    dataset.has_died = has_died(study_start_date)
    dataset.msoa = address_as_of(study_start_date).msoa_code
    dataset.imd = address_as_of(study_start_date).imd_rounded
    dataset.death_date = patients.date_of_death

    # Ethnicity in 6 categories
    dataset.ethnicity = clinical_events.where(clinical_events.ctv3_code.is_in(codelists.ethnicity)) \
        .sort_by(clinical_events.date) \
        .last_for_patient() \
        .ctv3_code.to_category(codelists.ethnicity)

    # covid tests
    dataset.latest_test_before_diagnosis = sgss_covid_all_tests \
        .where(sgss_covid_all_tests.is_positive) \
        .except_where(sgss_covid_all_tests.specimen_taken_date >= end_date - days(covid_to_longcovid_lag)) \
        .sort_by(sgss_covid_all_tests.specimen_taken_date).last_for_patient().specimen_taken_date

    dataset.all_test_positive = sgss_covid_all_tests \
        .where(sgss_covid_all_tests.is_positive) \
        .except_where(sgss_covid_all_tests.specimen_taken_date <= study_start_date) \
        .except_where(sgss_covid_all_tests.specimen_taken_date >= end_date - days(covid_to_longcovid_lag)) \
        .count_for_patient()

    # covid hospitalisation
    covid_hospitalisations = hospitalisation_diagnosis_matches(hospital_admissions, codelists.hosp_covid)

    dataset.first_covid_hosp = covid_hospitalisations \
        .sort_by(covid_hospitalisations.admission_date) \
        .first_for_patient().admission_date

    dataset.all_covid_hosp = covid_hospitalisations \
        .except_where(covid_hospitalisations.admission_date >= end_date - days(covid_to_longcovid_lag)) \
        .count_for_patient()

    # vaccine code
    create_sequential_variables(
      dataset,
      "covid_vacc_{n}_adm",
      num_variables=5,
      events=clinical_events.where(clinical_events.snomedct_code.is_in(codelists.vac_adm_combine)),
      column="date"
    )

    # Vaccines from the vaccines schema
    # only take one record per day to remove duplication
    all_vacc = vaccinations \
        .where(vaccinations.date < end_date - days(vaccine_to_longcovid_lag)) \
        .where(vaccinations.target_disease == "SARS-2 CORONAVIRUS")

    # this will be replaced with distinct_count_for_patient() once it is developed
    dataset.no_prev_vacc = all_vacc \
        .sort_by(vaccinations.date) \
        .count_for_patient()
    dataset.date_last_vacc = all_vacc.sort_by(all_vacc.date).last_for_patient().date
    dataset.last_vacc_gap = (dataset.pt_end_date - dataset.date_last_vacc).days

    # dataset.vacc_1 = all_vacc.sort_by(all_vacc.date).first_for_patient().date
    create_sequential_variables(
      dataset,
      "covid_vacc_{n}_vacc_tab",
      num_variables=6,
      events=all_vacc,
      column="date"
    )

    # Find the product name for each vaccine episode - will use this to check if they have all been the same or mixed types in analysis
    # Note - only checking for first 3 vaccines in this step
    create_sequential_variables(
      dataset,
      "covid_vacc_{n}_manufacturer_tab",
      num_variables=3,
      events=all_vacc,
      column="product_name"
    )

    # EXCLUSION criteria - gather these all here to remain consistent with the protocol
    population = population & (registrations_number == 1) & (dataset.age <= 100) & (dataset.age >= 16)  # will remove missing age

    dataset.define_population(population)
