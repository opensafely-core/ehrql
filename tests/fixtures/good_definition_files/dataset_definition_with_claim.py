# noqa: INP001
from ehrql import claim_permissions, create_dataset
from ehrql.tables.core import patients


claim_permissions("some_permission", "another_permission")

dataset = create_dataset()
dataset.year_of_birth = patients.date_of_birth.year
dataset.define_population(patients.exists_for_patient())
