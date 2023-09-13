from ehrql import Dataset, codelist_from_csv, months
from ehrql.tables.beta.tpp import clinical_events

diabetes_codelist = codelist_from_csv(XXX)
hba1c_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_diabetes_code_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(diabetes_codelist)
).sort_by(
        clinical_events.date
).first_for_patient().date

dataset.count_of_hba1c_tests_6mo_post_first_diabetes_code = clinical_events.where(
        clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.date.is_on_or_between(first_diabetes_code_date, first_diabetes_code_date + months(6))
).count_for_patient()
