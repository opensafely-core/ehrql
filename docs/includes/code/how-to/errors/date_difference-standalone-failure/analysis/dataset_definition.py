from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.age_in_may = "2023-05-01" - patients.date_of_birth
