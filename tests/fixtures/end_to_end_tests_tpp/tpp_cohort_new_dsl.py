from cohortextractor.concepts import tables
from cohortextractor.definition import Cohort, exists, pick_first_value, register


cohort = Cohort()
registrations = tables.registrations
population = registrations.select_column(
    registrations.patient_id
).make_one_row_per_patient(exists)
cohort.set_population(population)

events = tables.clinical_events
cohort.date = events.select_column(events.date).make_one_row_per_patient(
    pick_first_value
)
cohort.event = events.select_column(events.code).make_one_row_per_patient(
    pick_first_value
)
register(cohort)
