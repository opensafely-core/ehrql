from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)
asthma_review_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).sort_by(clinical_events.date).first_for_patient()

first_asthma_review = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_review_codelist)
).where(
        clinical_events.date.is_on_or_after(first_asthma_diagnosis)
).sort_by(clinical_events.date).first_for_patient()

dataset.weeks_between_diagnosis_and_review = (first_asthma_review - first_asthma_diagnosis).weeks
