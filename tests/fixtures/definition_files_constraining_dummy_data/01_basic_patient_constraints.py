# noqa: INP001
# From docs/tutorial/example-study/dataset_definition.py
# Constraints:
# - Patients table, sex and age

from ehrql import (
    codelist_from_csv,
    create_dataset,
)
from ehrql.tables.tpp import (
    patients,
    practice_registrations,
)


index_date = "2023-10-01"

dataset = create_dataset()
dataset.configure_dummy_data(population_size=10)

# codelists

ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    column="Code",
    category_column="Grouping_6",
)
# population variables

is_female_or_male = patients.sex.is_in(["female", "male"])

was_adult = (patients.age_on(index_date) >= 18) & (patients.age_on(index_date) <= 110)

was_alive = (
    patients.date_of_death.is_after(index_date) | patients.date_of_death.is_null()
)

was_registered = practice_registrations.for_patient_on(index_date).exists_for_patient()

dataset.define_population(is_female_or_male & was_adult & was_alive & was_registered)

# demographic variables

dataset.age = patients.age_on(index_date)

dataset.sex = patients.sex
