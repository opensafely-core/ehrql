from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
age = patients.age_on("2000-01-01")
age1 = patients.age_on("2023-01-01")
dataset.define_population(age > 16)
dataset.age = age
dataset.age1 = age1 # The second age feature now has a unique name on the dataset
