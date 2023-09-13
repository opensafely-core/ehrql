from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).first_for_patient()
dataset.first_asthma_diagnosis_code = first_asthma_diagnosis.snomedct_code
dataset.first_asthma_diagnosis_date = first_asthma_diagnosis.date
