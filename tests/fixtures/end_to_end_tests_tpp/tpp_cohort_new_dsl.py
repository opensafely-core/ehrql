from cohortextractor2.concepts import tables
from cohortextractor2.definition import register
from cohortextractor2.dsl import Cohort

cohort = Cohort()
cohort.set_population(tables.registrations.exists_for_patient())
events = tables.clinical_events
cohort.date = events.sort_by(events.date).first_for_patient().select_column(events.date)
cohort.event = (
    events.sort_by(events.code).first_for_patient().select_column(events.code)
)

register(cohort)
