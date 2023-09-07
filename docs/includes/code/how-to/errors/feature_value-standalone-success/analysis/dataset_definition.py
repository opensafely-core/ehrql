from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
latest_registration_per_patient = practice_registrations.sort_by(practice_registrations.start_date).last_for_patient()
dataset.registered_on = latest_registration_per_patient.start_date
