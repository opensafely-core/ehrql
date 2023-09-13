from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

hba1c_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.mean_hba1c = clinical_events.where(
        clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).numeric_value.mean_for_patient()
