from ehrql import Dataset
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
dataset.rural_urban = addresses.for_patient_on("2023-01-01").rural_urban_classification
