from datetime import date

from databuilder.ehrql import Dataset, days, years, months
from databuilder.tables.beta.tpp import (
    patients, addresses, appointments,
    practice_registrations, clinical_events,
    sgss_covid_all_tests, ons_deaths, 
)
from codelists import lc_codelists_combined

import codelists
import csv 

# study start date
study_start_date = date(2020, 11, 1)

# age 
age = (study_start_date - patients.date_of_birth).years


# Import the filtered GP list to exclude GP that was not using the long COVID codes
with open("output/dataset_lc_gp_list.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    lc_gp = [int(row["gp_practice"]) for row in reader]

target_practices = practice_registrations.where(practice_registrations.practice_pseudo_id.is_in(lc_gp))


# current registration
registration = practice_registrations \
    .except_where(practice_registrations.start_date > (study_start_date - months(3))) \
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date).last_for_patient()

# # historical registration
# historical_registration = practice_registrations \
#     .except_where(practice_registrations.start_date > date(2018, 11, 1)) \
#     .except_where(practice_registrations.end_date < date(2019, 11, 1))

# # covid tests
# latest_test_before_diagnosis = sgss_covid_all_tests \
#     .where(sgss_covid_all_tests.is_positive) \
#     .sort_by(sgss_covid_all_tests.specimen_taken_date).last_for_patient()

# Potential end of follow-up before matching
death_date = ons_deaths.sort_by(ons_deaths.date) \
    .last_for_patient().date
end_reg_date = registration.end_date
lc_dx_date = clinical_events.where(clinical_events.snomedct_code.is_in(lc_codelists_combined)) \
    .sort_by(clinical_events.date) \
    .first_for_patient().date # LC dx dates

dataset = Dataset()
dataset.define_population((age >= 18) & registration.exists_for_patient() & target_practices.exists_for_patient())
dataset.age = age
dataset.sex = patients.sex
dataset.region = registration.practice_stp
dataset.gp_practice = registration.practice_pseudo_id
dataset.registration_date = registration.start_date
# dataset.historical_comparison_group = historical_registration.exists_for_patient()
# dataset.comp_positive_covid_test = latest_test_before_diagnosis.exists_for_patient()
# dataset.date_of_latest_positive_test_before_diagnosis = latest_test_before_diagnosis.specimen_taken_date.to_first_of_month() # only need the month 
dataset.end_death = death_date
dataset.end_deregist = end_reg_date
dataset.long_covid_dx_date = lc_dx_date
