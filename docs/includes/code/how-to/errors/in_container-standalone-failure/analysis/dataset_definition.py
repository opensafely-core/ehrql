# --8<-- [start:initial_error]
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()

age = patients.age_on("2023-01-01")
dataset.age_30 = age.is_in(30)
# --8<-- [end:initial_error]
# --8<-- [start:age_range]
dataset.age_30_or_40 = age.is_in(30, 40)
# --8<-- [end:age_range]
