from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
registration = practice_registrations.for_patient_on("2023-01-01")
dataset.practice = registration.practice_pseudo_id
dataset.stp = registration.practice_stp
dataset.region = registration.nuts1_region_name
