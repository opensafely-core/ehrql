from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

cardiac_diagnosis_codes = codelist_from_csv(XXX)

dataset = Dataset()
dataset.last_cardiac_hospitalisation_date = medications.where(
        medications.dmd_code.is_in(cardiac_diagnosis_codes)
).where(
        medications.date.is_on_or_after("2022-07-01")
).sort_by(
        medications.date
).last_for_patient().date
