from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.date_of_birth = patients.date_of_birth
