from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.date_at_age_16 = patients.date_of_birth + 16
