# noqa: INP001
# Adapted from Schaffer et al.'s opioids-covid-research study
# Constraints:
# - Clinical events table: SNOMED code, date
# - Medications table: DMD code, date (multiple records consistent with each other)
from pathlib import Path

from ehrql import case, codelist_from_csv, create_dataset, when, years
from ehrql.tables.core import patients
from ehrql.tables.tpp import (
    addresses,
    clinical_events,
    medications,
    practice_registrations,
)


# Imported codelists
ethnicity_codelist_path = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "tutorial"
    / "example-study"
    / "codelists"
    / "opensafely-ethnicity.csv"
)
ethnicity_codelist = codelist_from_csv(
    ethnicity_codelist_path,
    column="Code",
    category_column="Grouping_6",
)


# Example codelists
class Namespace:
    pass


codelists = Namespace()
codelists.cancer_codes = ["94632009", "18105004"]
codelists.opioid_codes = [
    "21148211000001106",
    "42015111000001108",
    "36057211000001102",
    "4001411000001107",
]
codelists.hi_opioid_codes = ["36057211000001102", "4001411000001107"]
codelists.carehome_primis_codes = [
    "1024771000000108",
    "160734000",
    "160737007",
    "224224003",
    "248171000000108",
    "394923006",
]

index_date = "2022-04-01"
end_date = "2023-03-31"

dataset = create_dataset()

dataset.configure_dummy_data(population_size=10)

dataset.cancer = (
    clinical_events.where(clinical_events.snomedct_code.is_in(codelists.cancer_codes))
    .where(clinical_events.date.is_on_or_between(index_date - years(5), index_date))
    .exists_for_patient()
)

# Overall
dataset.opioid_any = (
    medications.where(medications.dmd_code.is_in(codelists.opioid_codes))
    .where(medications.date.is_on_or_between(index_date, end_date))
    .exists_for_patient()
)

# High dose / long-acting opioid
dataset.hi_opioid_any = (
    medications.where(medications.dmd_code.is_in(codelists.hi_opioid_codes))
    .where(medications.date.is_on_or_between(index_date, end_date))
    .exists_for_patient()
)

# Date of last prescription before index date
last_rx = (
    medications.where(medications.dmd_code.is_in(codelists.opioid_codes))
    .where(medications.date.is_before(index_date))
    .sort_by(medications.date)
    .last_for_patient()
    .date
)

# Is opioid naive using one year lookback (for denominator)
dataset.opioid_naive = last_rx.is_before(index_date - years(1)) | last_rx.is_null()

# Number of people with new prescriptions (among naive only)
dataset.opioid_new = (
    medications.where(medications.dmd_code.is_in(codelists.opioid_codes))
    .where(medications.date.is_on_or_between(index_date, end_date))
    .where(dataset.opioid_naive)
    .exists_for_patient()
)

# Define population #
dataset.define_population(
    (patients.age_on(index_date) >= 18)
    & (patients.age_on(index_date) < 110)
    & ((patients.sex == "male") | (patients.sex == "female"))
    & (patients.date_of_death.is_after(index_date) | patients.date_of_death.is_null())
    & (practice_registrations.for_patient_on(index_date).exists_for_patient())
)

# Demographics #

# Age for standardisation
age = patients.age_on("2022-04-01")

dataset.age_stand = case(
    when(age < 25).then("18-24"),
    when(age < 30).then("25-29"),
    when(age < 35).then("30-34"),
    when(age < 40).then("35-39"),
    when(age < 45).then("40-44"),
    when(age < 50).then("45-49"),
    when(age < 55).then("50-54"),
    when(age < 60).then("55-59"),
    when(age < 65).then("60-64"),
    when(age < 70).then("65-69"),
    when(age < 75).then("70-74"),
    when(age < 80).then("75-79"),
    when(age < 85).then("80-84"),
    when(age < 90).then("85-89"),
    when(age >= 90).then("90+"),
    otherwise="missing",
)

# Sex
dataset.sex = patients.sex

# IMD decile
imd = addresses.for_patient_on("2022-04-01").imd_rounded
dataset.imd10 = case(
    when((imd >= 0) & (imd < int(32844 * 1 / 10))).then("MD"),
    when(imd < int(32844 * 2 / 10)).then("2"),
    when(imd < int(32844 * 3 / 10)).then("3"),
    when(imd < int(32844 * 4 / 10)).then("4"),
    when(imd < int(32844 * 5 / 10)).then("5"),
    when(imd < int(32844 * 6 / 10)).then("6"),
    when(imd < int(32844 * 7 / 10)).then("7"),
    when(imd < int(32844 * 8 / 10)).then("8"),
    when(imd < int(32844 * 9 / 10)).then("9"),
    when(imd >= int(32844 * 9 / 10)).then("LD"),
    otherwise="unknown",
)

# Ethnicity
dataset.ethnicity = (
    clinical_events.where(clinical_events.ctv3_code.is_in(ethnicity_codelist))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(ethnicity_codelist)
)

# Practice region
dataset.region = practice_registrations.for_patient_on(
    "2022-04-01"
).practice_nuts1_region_name

# In care home based on primis codes/TPP address match
carehome_primis = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(codelists.carehome_primis_codes)
    )
    .where(clinical_events.date.is_on_or_before("2022-04-01"))
    .exists_for_patient()
)

carehome_tpp = addresses.for_patient_on("2022-04-01").care_home_is_potential_match

dataset.carehome = case(
    when(carehome_primis).then(True), when(carehome_tpp).then(True), otherwise=False
)
