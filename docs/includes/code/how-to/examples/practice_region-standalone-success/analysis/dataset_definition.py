from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
dataset.region = practice_registrations.for_patient_on("2023-01-01").nuts1_region_name
