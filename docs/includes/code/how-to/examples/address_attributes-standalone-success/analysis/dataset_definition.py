from ehrql import Dataset
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
address = addresses.for_patient_on("2023-01-01")
dataset.imd = address.imd
dataset.rural_urban_classification = address.rural_urban_classification
dataset.msoa = address.msoa
