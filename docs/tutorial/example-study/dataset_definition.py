from ehrql import (
    case,
    codelist_from_csv,
    create_dataset,
    days,
    when,
)
from ehrql.tables.core import (
    clinical_events,
    medications,
    patients,
    practice_registrations,
)

index_date = "2023-10-01"

dataset = create_dataset()

dataset.configure_dummy_data(population_size=10)

# codelists

ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6",
)

asthma_inhaler_codelist = codelist_from_csv(
    "codelists/opensafely-asthma-inhaler-salbutamol-medication.csv",
    column="code",
)

asthma_exacerbations_codelist = codelist_from_csv(
    "codelists/bristol-asthma-exacerbations.csv",
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

dataset.sex = patients.sex

age = patients.age_on(index_date)
dataset.age_band = case(
    when((age >= 18) & (age < 50)).then("age_18_49"),
    when((age >= 50) & (age < 65)).then("age_50_64"),
    when((age >= 65) & (age < 75)).then("age_65_74"),
    when((age >= 75) & (age < 85)).then("age_75_84"),
    when((age >= 85)).then("age_85_plus"),
)

dataset.ethnicity = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(
            ethnicity_codelist
        )
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code.to_category(ethnicity_codelist)
)

# exposure variables

dataset.num_asthma_inhaler_medications = medications.where(
    medications.dmd_code.is_in(asthma_inhaler_codelist)
    & medications.date.is_on_or_between(
        index_date - days(30), index_date
    )
).count_for_patient()

# outcome variables

dataset.date_of_first_asthma_exacerbation = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(
            asthma_exacerbations_codelist
        )
    )
    .where(clinical_events.date.is_after(index_date))
    .sort_by(clinical_events.date)
    .first_for_patient()
    .date
)
