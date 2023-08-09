from ehrql import Dataset

# --8<-- [start:import]
from ehrql.tables.beta.core import patients


# --8<-- [end:import]

# --8<-- [start:date_of_birth_column]
dob = patients.date_of_birth
# --8<-- [end:date_of_birth_column]

dataset = Dataset()
dataset.define_population(dob.year < 2000)
