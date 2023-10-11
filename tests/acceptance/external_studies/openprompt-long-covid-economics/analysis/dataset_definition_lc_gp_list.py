from datetime import date

from databuilder.ehrql import Dataset, days, years
from databuilder.tables.beta.tpp import (
    patients, practice_registrations, clinical_events,
)
from codelists import lc_codelists_combined

# Patients with long covid diagnoses
lc_dx = clinical_events.where(clinical_events.snomedct_code.is_in(lc_codelists_combined)) \
    .sort_by(clinical_events.date) \
    .first_for_patient()

# current registration; do not exclude less than 1 year registration.
registration = practice_registrations \
    .except_where(practice_registrations.end_date <= date(2020, 11, 1)) \
    .sort_by(practice_registrations.start_date).last_for_patient()

dataset = Dataset()
dataset.define_population(lc_dx.exists_for_patient())
dataset.gp_practice = registration.practice_pseudo_id

dataset.configure_dummy_data(population_size=30000)
