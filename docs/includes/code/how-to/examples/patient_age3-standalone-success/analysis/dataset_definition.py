from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

index_date = "2023-01-01"
dataset = Dataset()
dataset.age = patients.age_on(index_date)
