from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.last_asthma_diagnosis_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).last_for_patient().date
