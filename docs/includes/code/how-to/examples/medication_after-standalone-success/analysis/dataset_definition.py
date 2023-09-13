from ehrql import Dataset, codelist_from_csv, weeks
from ehrql.tables.beta.tpp import clinical_events, medications

asthma_codelist = codelist_from_csv(XXX)
inhaled_corticosteroid_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_asthma_diagnosis_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).first_for_patient().date
dataset.first_asthma_diagnosis_date = first_asthma_diagnosis_date
dataset.count_ics_prescriptions_2wks_post_diagnosis = medications.where(
        medications.dmd_code.is_in(inhaled_corticosteroid_codelist)
).where(
        medications.date.is_on_or_between(first_asthma_diagnosis_date,first_asthma_diagnosis_date + weeks(2))
)
