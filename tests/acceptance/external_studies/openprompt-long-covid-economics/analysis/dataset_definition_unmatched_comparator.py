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


# Import the filtered GP list to exclude GP that was not using the long COVID codes
with open("output/dataset_lc_gp_list.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    lc_gp = [int(row["gp_practice"]) for row in reader]

target_practices = practice_registrations.where(practice_registrations.practice_pseudo_id.is_in(lc_gp))

dataset = Dataset()
dataset.define_population(
    (age>= 18) & (age <=100) 
    & (registrations_number == 1) 
    & registration.exists_for_patient() 
    & target_practices.exists_for_patient()
    & patients.sex.contains("male")
    & (death_date.is_after(study_start_date))
    & (end_reg_date.is_after(study_start_date))
    & (lc_cure_date.is_after(study_start_date))        
)
dataset.age = age
dataset.sex = patients.sex
dataset.region = registration.practice_nuts1_region_name
dataset.registration_date = registration.start_date
dataset.long_covid_dx = lc_dx.exists_for_patient().map_values({True: 1, False: 0})
dataset.long_covid_dx_date = lc_dx_date
dataset.end_death = death_date
dataset.end_deregist = end_reg_date
dataset.end_lc_cure = lc_cure_date
dataset.configure_dummy_data(population_size=50000)
