from datetime import date

from databuilder.ehrql import Dataset, days, years
from databuilder.tables.beta.tpp import (
    patients, ec_cost, opa_cost
)
from ehrql.tables.beta.raw.tpp import apcs_cost_historical

study_start_date = date(2020, 11, 1)
study_one_year = date(2021, 11, 1)
study_two_year = date(2022, 11, 1)
study_end_date = date(2023, 1, 31)

age = (study_start_date - patients.date_of_birth).years

# Query total apc costs:
apc_cost_1y = apcs_cost_historical \
    .where((apcs_cost_historical.admission_date >= study_start_date) &
           (apcs_cost_historical.admission_date < study_one_year)) \
    .grand_total_payment_mff.sum_for_patient()

apc_cost_2y = apcs_cost_historical \
    .where((apcs_cost_historical.admission_date >= study_one_year) &
           (apcs_cost_historical.admission_date < study_two_year)) \
    .grand_total_payment_mff.sum_for_patient()

apc_cost_total = apcs_cost_historical \
    .where((apcs_cost_historical.admission_date >= study_start_date) &
           (apcs_cost_historical.admission_date < study_end_date)) \
    .grand_total_payment_mff.sum_for_patient()

# Query total EC costs:
ec_cost_1y = ec_cost \
    .where((ec_cost.arrival_date >= study_start_date) & 
           (ec_cost.arrival_date < study_one_year)) \
    .grand_total_payment_mff.sum_for_patient()

ec_cost_2y = ec_cost\
    .where((ec_cost.arrival_date >= study_one_year) &
           (ec_cost.arrival_date < study_two_year)) \
    .grand_total_payment_mff.sum_for_patient()

ec_cost_total = ec_cost \
    .where((ec_cost.arrival_date >= study_start_date) &
           (ec_cost.arrival_date < study_end_date)) \
    .grand_total_payment_mff.sum_for_patient()

# Query total OPA costs:
opa_cost_1y = opa_cost \
    .where((opa_cost.appointment_date>= study_start_date) & 
           (opa_cost.appointment_date< study_one_year)) \
    .grand_total_payment_mff.sum_for_patient()

opa_cost_2y = opa_cost\
    .where((opa_cost.appointment_date>= study_one_year) &
           (opa_cost.appointment_date< study_two_year)) \
    .grand_total_payment_mff.sum_for_patient()

opa_cost_total = opa_cost \
    .where((opa_cost.appointment_date  >= study_start_date) &
           (opa_cost.appointment_date  < study_end_date)) \
    .grand_total_payment_mff.sum_for_patient()


# Define dataset:
dataset = Dataset()
dataset.define_population(
    (age>=18)
    & (age<=100) 
    & (patients.sex.contains("male"))
)
dataset.apc_cost_1y = apc_cost_1y
dataset.apc_cost_2y = apc_cost_2y
dataset.apc_cost_total = apc_cost_total
dataset.ec_cost_1y = ec_cost_1y
dataset.ec_cost_2y = ec_cost_2y
dataset.ec_cost_total = ec_cost_total
dataset.opa_cost_1y = opa_cost_1y
dataset.opa_cost_2y = opa_cost_2y
dataset.opa_cost_total = opa_cost_total