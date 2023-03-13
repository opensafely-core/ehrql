from datetime import date

from databuilder.ehrql import Dataset, days, years
from databuilder.tables.beta.tpp import (
    patients, addresses, appointments,
    practice_registrations, clinical_events,
    sgss_covid_all_tests, ons_deaths, hospital_admissions,
)
from databuilder.codes import SNOMEDCTCode
from codelists import lc_codelists_combined
import codelists
from variables import add_visits

study_start_date = date(2020, 11, 1)

# age 
age = (study_start_date - patients.date_of_birth).years

# current registration
registration = practice_registrations \
    .except_where(practice_registrations.start_date > study_start_date - years(1)) \
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date).last_for_patient()

# long covid diagnoses
lc_dx = clinical_events.where(clinical_events.snomedct_code.is_in(lc_codelists_combined)) \
    .sort_by(clinical_events.date) \
    .first_for_patient() # had lc dx and dx dates

# covid tests month
latest_test_before_diagnosis = sgss_covid_all_tests \
    .where(sgss_covid_all_tests.is_positive) \
    .except_where(sgss_covid_all_tests.specimen_taken_date >= lc_dx.date - days(30)) \
    .sort_by(sgss_covid_all_tests.specimen_taken_date) \
    .last_for_patient()
# # only need the diagnostic month for sensitivity analysis matching

# define end date: lc dx date +12 | death | derigistration | post COVID-19 syndrome resolved
one_year_after_start = lc_dx.date + days(365) 
death_date = ons_deaths.sort_by(ons_deaths.date) \
    .last_for_patient().date
end_reg_date = registration.end_date
lc_cure = clinical_events.where(clinical_events.snomedct_code ==  SNOMEDCTCode("1326351000000108")) \
    .sort_by(clinical_events.date) \
    .first_for_patient()
# #first recorded lc cure date


dataset = Dataset()
dataset.define_population((age >= 18) & registration.exists_for_patient() & lc_dx.exists_for_patient())
dataset.age = age
dataset.sex = patients.sex
dataset.region = registration.practice_stp
dataset.gp_practice = registration.practice_pseudo_id
dataset.registration_date = registration.start_date
dataset.covid_positive = latest_test_before_diagnosis.exists_for_patient()
dataset.covid_dx_month = latest_test_before_diagnosis.specimen_taken_date.to_first_of_month() # only need dx month
dataset.long_covid_dx = lc_dx.exists_for_patient()
dataset.long_covid_dx_date = lc_dx.date
dataset.index_date = lc_dx.date
dataset.end_1y_after_index = one_year_after_start
dataset.end_death = death_date
dataset.end_deregist = end_reg_date
dataset.end_lc_cure = lc_cure.date

add_visits(dataset, lc_dx.date, num_months=1)
add_visits(dataset, lc_dx.date, num_months=2)
add_visits(dataset, lc_dx.date, num_months=3)
add_visits(dataset, lc_dx.date, num_months=4)
add_visits(dataset, lc_dx.date, num_months=5)
add_visits(dataset, lc_dx.date, num_months=6)
add_visits(dataset, lc_dx.date, num_months=7)
add_visits(dataset, lc_dx.date, num_months=8)
add_visits(dataset, lc_dx.date, num_months=9)
add_visits(dataset, lc_dx.date, num_months=10)
add_visits(dataset, lc_dx.date, num_months=11)
add_visits(dataset, lc_dx.date, num_months=12)


