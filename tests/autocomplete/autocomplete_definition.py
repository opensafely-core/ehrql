# noqa: INP001
from ehrql.tables.core import clinical_events, patients
from ehrql.tables.tpp import addresses, apcs, ons_deaths


# A file to keep track of things where we get good autocomplete
# behaviour. At some point we could try and create tests for this
# but it's tricky.

# Currently all columns on all tables have type of "Series | Any",
# so we don't get autocomplete. Providing type hints on the Series
# class, and on the @table decorator means the column types are
# correct e.g. IntPatientSeries, DateEventSeries etc. and therefore
# we get autocomplete for all the properties and methods on each series.
patients.date_of_birth  # DatePatientSeries
patients.sex  # StrPatientSeries
ons_deaths.underlying_cause_of_death  # CodePatientSeries

clinical_events.date  # DateEventSeries
clinical_events.numeric_value  # FloatEventSeries
clinical_events.snomedct_code  # CodeEventSeries
apcs.all_diagnoses  # MultiCodeStringEventSeries

addresses.has_postcode  # BoolEventSeries
addresses.address_id  # IntEventSeries
