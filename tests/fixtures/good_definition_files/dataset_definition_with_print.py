# noqa: INP001
from ehrql import create_dataset
from ehrql.tables.core import patients


dataset = create_dataset()
dataset.year_of_birth = patients.date_of_birth.year
dataset.sex = patients.sex
dataset.define_population(patients.date_of_birth.is_on_or_after("2000-01-01"))
print("user stdout")
