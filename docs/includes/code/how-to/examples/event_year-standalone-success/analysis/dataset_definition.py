from datetime import date
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.year_of_first = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).sort_by(
        clinical_events.date
).first_for_patient().date.year
