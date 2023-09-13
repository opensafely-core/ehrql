from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_had_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).exists_for_patient()
