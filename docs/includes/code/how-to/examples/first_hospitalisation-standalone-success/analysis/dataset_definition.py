from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import hospital_admissions

cardiac_diagnosis_codes = codelist_from_csv(XXX)

dataset = Dataset()
dataset.first_cardiac_hospitalisation_date = hospital_admissions.where(
        hospital_admissions.snomedct_code.is_in(cardiac_diagnosis_codes)
).where(
        hospital_admissions.date.is_on_or_after("2022-07-01")
).sort_by(
        hospital_admissions.date
).first_for_patient().date
