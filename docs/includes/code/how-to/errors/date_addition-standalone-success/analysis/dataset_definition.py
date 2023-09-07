from ehrql import Dataset, years
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.date_at_age_16 = patients.date_of_birth + years(16)
