from cohortextractor.concepts import tables
from cohortextractor.definition import Cohort, pick_first_value, register


cohort = Cohort()
events = tables.clinical_events
cohort.date = events.select_column(events.date).make_one_row_per_patient(
    pick_first_value
)
cohort.event = events.select_column(events.code).make_one_row_per_patient(
    pick_first_value
)
register(cohort)
