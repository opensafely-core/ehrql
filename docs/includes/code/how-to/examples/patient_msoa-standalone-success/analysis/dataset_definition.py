from ehrql import Dataset
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
dataset.msoa = addresses.for_patient_on("2023-01-01").msoa
