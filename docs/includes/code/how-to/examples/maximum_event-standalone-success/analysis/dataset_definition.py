from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

hba1c_codelist = codelist_from_csv(XXX)

dataset = Dataset()
max_hba1c = clinical_events.where(
        clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).numeric_value.maximum_for_patient()

dataset.date_of_max_hba1c_observed = clinical_events.where(clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.numeric_value == max_hba1c
).sort_by(
        clinical_events.date
).last_for_patient().date
