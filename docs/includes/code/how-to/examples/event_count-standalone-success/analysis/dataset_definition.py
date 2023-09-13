from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

statin_medications = codelist_from_csv(XXX)

dataset = Dataset()
dataset.number_of_statin_prescriptions_in_last_year = medications.where(
        medications.dmd_code.is_in(statin_medications)
).where(
        medications.is_on_or_between("2022-01-01", "2023-01-01")
).count_for_patient()
