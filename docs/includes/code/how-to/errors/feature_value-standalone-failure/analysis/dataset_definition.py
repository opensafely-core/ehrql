from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
dataset.registered_on = practice_registrations.sort_by(practice_registrations.start_date).last_for_patient()
