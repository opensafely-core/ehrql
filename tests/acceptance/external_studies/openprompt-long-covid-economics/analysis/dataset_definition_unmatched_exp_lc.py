from datetime import date

from databuilder.ehrql import Dataset, days, years
from databuilder.tables.beta.tpp import (
    patients, addresses, ons_deaths, sgss_covid_all_tests,
    practice_registrations, clinical_events,
)
from databuilder.codes import SNOMEDCTCode
from codelists import lc_codelists_combined
from covariates import *

# Defining the exposure groups (before matching)

dataset = Dataset()
dataset.define_population(
    (age>=18)
    & (age<=100) 
    & (registrations_number == 1) 
    & registration.exists_for_patient() 
    & lc_dx.exists_for_patient()
    & (patients.sex.contains("male"))
    & (death_date.is_after(lc_dx_date))
    & (end_reg_date.is_after(lc_dx_date))
    & (lc_cure_date.is_after(lc_dx_date))    
)
dataset.age = age
dataset.sex = patients.sex
dataset.region = registration.practice_nuts1_region_name
dataset.registration_date = registration.start_date
dataset.long_covid_dx = lc_dx.exists_for_patient().map_values({True: 1, False: 0})
dataset.long_covid_dx_date = lc_dx_date
dataset.index_date = lc_dx_date
dataset.end_death = death_date
dataset.end_deregist = end_reg_date
dataset.end_lc_cure = lc_cure_date
dataset.configure_dummy_data(population_size=50000)
