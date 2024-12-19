# noqa: INP001
from ehrql import days, weeks
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


# There are loads of things that return a series where the typ
# (int, str, float etc.) is fixed, but it can be a PatientSeries
# or an EventSeries depending on whether the calling object is a
# PatientSeries or an EventSeries. This can be achieved with two
# overloaded methods and type hints

#
# BaseSeries
#
base_eq = patients.sex == patients.date_of_birth  # BoolPatientSeries
base_ne = clinical_events.date != clinical_events.numeric_value  # BoolEventSeries
patients.sex.is_null()  # BoolPatientSeries
clinical_events.date.is_not_null()  # BoolEventSeries
patients.sex.is_in([])  # BoolPatientSeries
clinical_events.snomedct_code.is_not_in([])  # BoolEventSeries

#
# ComparableFunctions
#
comparable_lt = (
    clinical_events.numeric_value < clinical_events.numeric_value
)  # BoolEventSeries
comparable_le = (
    clinical_events.numeric_value <= clinical_events.numeric_value
)  # BoolEventSeries
comparable_gt = (
    clinical_events.numeric_value > clinical_events.numeric_value
)  # BoolEventSeries
comparable_ge = (
    clinical_events.numeric_value >= clinical_events.numeric_value
)  # BoolEventSeries

#
# StrFunctions
#
patients.sex.contains("m")  # BoolPatientSeries

#
# NumericFunctions
#
numeric_truediv = clinical_events.numeric_value / 10  # FloatEventSeries
numeric_rtruediv = 10 / clinical_events.numeric_value  # FloatEventSeries
numeric_floordiv = clinical_events.numeric_value // 10  # IntEventSeries
numeric_rfloordiv = 10 // clinical_events.numeric_value  # IntEventSeries
clinical_events.numeric_value.as_int()  # IntEventSeries
clinical_events.numeric_value.as_float()  # FloatEventSeries

#
# DateFunctions
#
patients.date_of_birth.is_before()  # BoolPatientSeries
patients.date_of_birth.is_on_or_before()  # BoolPatientSeries
patients.date_of_birth.is_after()  # BoolPatientSeries
patients.date_of_birth.is_on_or_after()  # BoolPatientSeries
clinical_events.date.is_between_but_not_on()  # BoolEventSeries
clinical_events.date.is_on_or_between()  # BoolEventSeries
clinical_events.date.is_during()  # BoolEventSeries


#
# MultiCodeStringFunctions
#
apcs.all_diagnoses.contains("N13")  # BoolEventSeries
apcs.all_diagnoses.contains_any_of([])  # BoolEventSeries

#
# Couple of random list[tuple] types
starting_on = weeks(3).starting_on("2000-01-01")[0][0]  # date
ending_on = weeks(3).ending_on("2000-01-01")[0][0]  # date
