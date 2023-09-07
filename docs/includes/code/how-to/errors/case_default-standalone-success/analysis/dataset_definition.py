from ehrql import Dataset
from ehrql.tables.beta.tpp import case, patients, when

dataset = Dataset()

age = patients.age_on("2023-01-01")
dataset.age_group = case(
   when(age < 10).then(1),
   when(age > 80).then(2),
   default=0,
)
