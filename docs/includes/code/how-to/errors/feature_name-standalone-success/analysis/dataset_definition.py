from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.age = patients.age_on("2023-01-01") # We have changed the invalid feature name, "age!", to a valid one, "age".
