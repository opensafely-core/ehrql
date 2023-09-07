from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
age = patients.age_on("2023-01-01")
dataset.define_population(age >= 10)  # age is now being compared to the integer 10
