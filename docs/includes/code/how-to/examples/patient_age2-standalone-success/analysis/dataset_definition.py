from datetime import date
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.age = patients.age_on(date(2023, 1, 1))
