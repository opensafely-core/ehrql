from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.age = patients.age_on("2023-01-01")
dataset.define_population(dataset.age > 16) # Here we have now defined a population for the dataset.
