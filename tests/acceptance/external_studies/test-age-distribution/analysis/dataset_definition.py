from ehrql import create_dataset
from ehrql.tables.smoketest import patients

index_year = 2022
min_age = 18
max_age = 80

year_of_birth = patients.date_of_birth.year
age = index_year - year_of_birth

dataset = create_dataset()
dataset.define_population((age >= min_age) & (age <= max_age))
dataset.age = age
