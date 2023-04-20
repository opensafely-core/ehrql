# --8<-- [start:minimalehrqlimportpatients]
from ehrql.tables.beta.smoketest import patients

year_of_birth = patients.date_of_birth.year
# --8<-- [end:minimalehrqlimportpatients]

# --8<-- [start:minimalehrql]
from ehrql.ehrql import Dataset
from ehrql.tables.beta.smoketest import patients

year_of_birth = patients.date_of_birth.year
dataset = Dataset()
dataset.define_population(year_of_birth >= 2000)
dataset.year_of_birth = year_of_birth
# --8<-- [end:minimalehrql]
