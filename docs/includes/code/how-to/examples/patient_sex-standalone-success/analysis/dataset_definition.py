from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.sex = patients.sex
