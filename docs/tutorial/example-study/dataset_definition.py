from ehrql import (
    case,
    codelist_from_csv,
    create_dataset,
    days,
    when,
)
from ehrql.tables.tpp import (
    addresses,
    clinical_events,
    apcs,
    medications,
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

asthma_inhaler_codelist = codelist_from_csv(
    "codelists/opensafely-asthma-inhaler-salbutamol-medication.csv",
    column="code",
)

# population variables

is_female_or_male = patients.sex.is_in(["female", "male"])

was_adult = (patients.age_on(index_date) >= 18) & (
    patients.age_on(index_date) <= 110
)

was_alive = (
    patients.date_of_death.is_after(index_date)
    | patients.date_of_death.is_null()
)

was_registered = practice_registrations.for_patient_on(
    index_date
).exists_for_patient()

dataset.define_population(
    is_female_or_male
    & was_adult
    & was_alive
    & was_registered
)

# demographic variables

dataset.age = patients.age_on(index_date)

dataset.sex = patients.sex

dataset.ethnicity = (
    clinical_events.where(
        clinical_events.ctv3_code.is_in(ethnicity_codelist)
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(ethnicity_codelist)
)

imd_rounded = addresses.for_patient_on(
    index_date
).imd_rounded
max_imd = 32844
dataset.imd_quintile = case(
    when(imd_rounded < int(max_imd * 1 / 5)).then(1),
    when(imd_rounded < int(max_imd * 2 / 5)).then(2),
    when(imd_rounded < int(max_imd * 3 / 5)).then(3),
    when(imd_rounded < int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
)

# exposure variables

dataset.num_asthma_inhaler_medications = medications.where(
    medications.dmd_code.is_in(asthma_inhaler_codelist)
    & medications.date.is_on_or_between(
        index_date - days(30), index_date
    )
).count_for_patient()

# outcome variables

dataset.date_of_first_admission = (
    apcs.where(
        apcs.admission_date.is_after(
            index_date
        )
    )
    .sort_by(apcs.admission_date)
    .first_for_patient()
    .admission_date
)
