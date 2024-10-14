# noqa: INP001
# Adapted from Schaffer et al.'s opioids-covid-research study
# Constraints:
# - Clinical events table: SNOMED code, date
# - Medications table: DMD code, date (multiple records consistent with each other)
from ehrql import create_dataset, years
from ehrql.tables.core import patients
from ehrql.tables.tpp import (
    clinical_events,
    medications,
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

index_date = "2023-10-01"
end_date = "2023-12-31"

dataset = create_dataset()

dataset.configure_dummy_data(population_size=100)

dataset.define_population(patients.date_of_birth.is_on_or_before("2023-12-31"))

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
