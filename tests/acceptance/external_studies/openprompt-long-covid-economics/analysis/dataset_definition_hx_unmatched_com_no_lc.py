from datetime import date

from databuilder.ehrql import Dataset, days, years, months
from databuilder.tables.beta.tpp import (
    patients, addresses, appointments,
    practice_registrations, clinical_events,
    sgss_covid_all_tests, ons_deaths, 
)
from codelists import lc_codelists_combined
from covariates import *
import codelists
import csv 

# Defining the historical exposure groups (before matching) 
study_start_date = date(2020, 11, 1)
study_end_date = date(2023, 1, 31)
hx_study_start_date = date(2019, 3, 1)
hx_study_end_date = date(2020, 3, 1)

# Import the filtered GP list to exclude GP that was not using the long COVID codes
with open("output/dataset_lc_gp_list.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    lc_gp = [int(row["gp_practice"]) for row in reader]

target_practices = practice_registrations.where(practice_registrations.practice_pseudo_id.is_in(lc_gp))

# Registration data: registered on study_start_date & registered on hx_study_start_date
had_hx_registration = practice_registrations \
    .where(practice_registrations.start_date <= hx_study_start_date) \
    .except_where(practice_registrations.end_date <= study_start_date) \
    .sort_by(practice_registrations.start_date).last_for_patient()

# had long COVID (after start date) 
lc_dx = clinical_events.where(clinical_events.snomedct_code.is_in(lc_codelists_combined)) \
    .where(clinical_events.date >= study_start_date) \
    .where(clinical_events.date <= study_end_date) \
    .sort_by(clinical_events.date) \
    .first_for_patient()# had lc dx and dx dates

# other demographic vars for matching
age = (study_start_date - patients.date_of_birth).years

dataset = Dataset()
dataset.define_population(
    had_hx_registration.exists_for_patient()
    & registration.exists_for_patient()
    & (registrations_number == 1) 
    & ~lc_dx.exists_for_patient()
    & (age>= 18) 
    & (age <=100)
    & (patients.sex.contains("male"))
    & (death_date.is_after(study_start_date))
    & (end_reg_date.is_after(study_start_date))
    & (lc_cure_date.is_after(study_start_date))    
)
dataset.age = age
dataset.sex = patients.sex
dataset.lc_exp = lc_dx.exists_for_patient().map_values({True: 1, False: 0})
dataset.region = registration.practice_nuts1_region_name
dataset.end_death = death_date
dataset.end_deregist = end_reg_date
dataset.end_lc_cure = lc_cure_date

dataset.configure_dummy_data(population_size=10000)
