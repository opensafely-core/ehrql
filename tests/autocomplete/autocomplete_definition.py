# noqa: INP001
from ehrql import days
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


# There are some methods that always return the same type
clinical_events.snomedct_code.count_distinct_for_patient()  # IntPatientSeries
clinical_events.numeric_value.mean_for_patient()  # FloatPatientSeries
clinical_events.date.count_episodes_for_patient()  # IntPatientSeries
patients.exists_for_patient()  # BoolPatientSeries
patients.count_for_patient()  # IntPatientSeries
days(100) == days(100)  # bool
days(100) != days(100)  # bool

# There are some things that return the same type as the calling
# object or one of the arguments

bool_and = (
    patients.exists_for_patient() & patients.exists_for_patient()
)  # BoolPatientSeries
bool_or = (
    patients.exists_for_patient() | patients.exists_for_patient()
)  # BoolPatientSeries
bool_invert = ~patients.exists_for_patient()  # BoolPatientSeries
numeric_neg = -clinical_events.numeric_value  # FloatEventSeries
clinical_events.date.to_first_of_year()  # DateEventSeries
patients.date_of_birth.to_first_of_month()  # DatePatientSeries
duration_negation = -days(100)  # days
patients.sex.when_null_then(patients.sex)  # StrPatientSeries
duration_add = days(100) + patients.date_of_birth  # DatePatientSeries
duration_radd = clinical_events.date + days(100)  # DateEventSeries
duration_add_duration = days(100) + days(100)  # days
duration_rsub = clinical_events.date - days(100)  # DateEventSeries
# !!! the above doesn't work and thinks its a DateDifference. I assume
# !!! because the NotImplemented on the DateFunctions __sub__ method
# !!! is only known at runtime
duration_sub_duration = days(100) - days(100)  # days
