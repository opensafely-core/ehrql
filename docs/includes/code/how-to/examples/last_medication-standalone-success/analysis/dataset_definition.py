from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

statin_medications = codelist_from_csv(XXX)

dataset = Dataset()
dataset.last_statin_prescription_date = medications.where(
        medications.dmd_code.is_in(statin_medications)
).where(
        medications.date.is_on_or_after("2022-07-01")
).sort_by(
        medications.date
).last_for_patient().date
