from databuilder.definition import register
from databuilder.dsl import Cohort
from databuilder.frames import clinical_events as events
from databuilder.frames import practice_registrations as registrations

cohort = Cohort()
cohort.set_population(registrations.exists_for_patient())
cohort.date = events.sort_by(events.date).first_for_patient().select_column(events.date)
cohort.event = (
    events.sort_by(events.code).first_for_patient().select_column(events.code)
)

register(cohort)
