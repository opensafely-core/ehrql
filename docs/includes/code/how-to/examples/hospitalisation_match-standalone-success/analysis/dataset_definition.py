from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import hospital_admissions

cardiac_diagnosis_codes = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_recent_cardiac_admission = hospital_admissions.where(
        hospital_admissions.primary_diagnoses .is_in(cardiac_diagnosis_codes)
).where(
        hospital_admissions.is_on_or_between("2022-07-01", "2023-01-01")
).exists_for_patient()
