from ehrql import Dataset
from ehrql.tables.beta.core import patients


dataset = Dataset()
dataset.define_population(patients.date_of_birth.year < 2000)
