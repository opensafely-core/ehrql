from ehrql import Dataset
# --8<-- [start:tables_import]
from ehrql.tables.beta.tpp import addresses, patients
# --8<-- [end:tables_import]

dataset = Dataset()
dataset.define_population(patients.date_of_birth.year < 2000)
dataset.imd_rounded = addresses.sort_by(addresses.start_date).last_for_patient().imd_rounded
