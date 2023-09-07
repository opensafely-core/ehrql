from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.age_greater_than_16 = patients.age_on("2023-01-01") > 16
