from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()

age = patients.age_on("2023-01-01")
dataset.age_30_list = age.is_in([30])
dataset.age_30_or_40_set = age.is_in({30, 40})
dataset.age_30_or_40_tuple = age.is_in((30, 40))
