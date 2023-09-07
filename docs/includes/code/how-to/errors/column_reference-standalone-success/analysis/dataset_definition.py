from ehrql import Dataset
from ehrql.tables.beta.tpp import clinical_events

dataset = Dataset()
first_event = clinical_events.sort_by(clinical_events.date).first_for_patient()
dataset.event_date = first_event.date
