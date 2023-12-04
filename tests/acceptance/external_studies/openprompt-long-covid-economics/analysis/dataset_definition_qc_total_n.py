from datetime import date

from databuilder.ehrql import Dataset, days, years, months
from databuilder.tables.beta.tpp import (
    patients, addresses, appointments,
    practice_registrations, clinical_events, ons_deaths, 
)
from codelists import lc_codelists_combined
from covariates import *

# For Total eligible N

dataset = Dataset()
dataset.define_population(
    (age>= 18) & (age <=100) 
    & (registrations_number == 1) 
    & registration.exists_for_patient() 
    & patients.sex.contains("male")
    & (death_date.is_after(study_start_date))
    & (end_reg_date.is_after(study_start_date))  
)
dataset.sex = patients.sex