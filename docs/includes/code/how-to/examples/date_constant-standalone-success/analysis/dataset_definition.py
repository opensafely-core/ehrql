from ehrql import Dataset, codelist_from_csv, weeks
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

index_date = "2022-07-01"

dataset = Dataset()
dataset.has_recent_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_between(index_date, index_date + weeks(2))
).exists_for_patient()
