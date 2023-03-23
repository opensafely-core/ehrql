from databuilder.ehrql import case, when

# I'm importing from a separate `measures` module here, but I think there's an argument
# that this should all be importable from the `ehrql` namespace
from databuilder.measures import (
    INTERVAL_END_DATE,
    INTERVAL_START_DATE,
    Intervals,
    Measure,
)
from databuilder.tables.beta.tpp import (
    clinical_events,
    ons_deaths,
    patients,
    practice_registrations,
)

# Note that the INTERVAL_START_DATE/INTERVAL_END_DATE values are ehrQL parameters (or
# placeholders). From the point of view of the rest of ehrQL they are just
# `DatePatientSeries` instances like any other. But they have no date associated with
# them and so can't be executed until we substitue in a concrete date value.
#
# We're using a start/end pair rather than a single INDEX_DATE so we don't have to
# hardcode the interval duration into the definition.
#
# I used uppercase for these names as they are, technically, constants. But I'm open to
# the accusation that this is all a bit Java and it would be more readable if they were
# lowercase.


# DEMOGRAPHICS
#

practice = practice_registrations.for_patient_on(INTERVAL_START_DATE)

has_died = ons_deaths.where(ons_deaths.date <= INTERVAL_START_DATE).exists_for_patient()

age = patients.age_on(INTERVAL_START_DATE)

age_band = case(
    when((age >= 0) & (age <= 4)).then("0-4"),
    when((age >= 5) & (age <= 9)).then("5-9"),
    when((age >= 10) & (age <= 14)).then("10-14"),
    when((age >= 15) & (age <= 19)).then("15-19"),
    when((age >= 20) & (age <= 24)).then("20-24"),
    when((age >= 25) & (age <= 29)).then("25-29"),
    when((age >= 30) & (age <= 34)).then("30-34"),
    when((age >= 35) & (age <= 39)).then("35-39"),
    when((age >= 40) & (age <= 44)).then("40-44"),
    when((age >= 45) & (age <= 49)).then("45-49"),
    when((age >= 50) & (age <= 54)).then("50-54"),
    when((age >= 55) & (age <= 59)).then("55-59"),
    when((age >= 60) & (age <= 64)).then("60-64"),
    when((age >= 65) & (age <= 69)).then("65-69"),
    when((age >= 70) & (age <= 74)).then("70-74"),
    when((age >= 75) & (age <= 79)).then("75-79"),
    when((age >= 80) & (age <= 84)).then("80-84"),
    when((age >= 85) & (age <= 89)).then("85-89"),
    when(age >= 90).then("90plus"),
    default="missing",
)


# DENOMINATOR
#

population = (
    practice.exists_for_patient()
    & ~has_died
    & patients.sex.is_in(["male", "female"])
    & (age_band != "missing")
)


# NUMERATOR
#
# Patients who have had a matching event in the interval

# https://www.opencodelists.org/codelist/primis-covid19-vacc-uptake/cov1decl/v1.1/
codelist = [
    "1324721000000108",  # Severe acute respiratory syndrome coronavirus 2 vaccination dose declined
    "1324741000000101",  # Severe acute respiratory syndrome coronavirus 2 vaccination first dose declined
    "1324811000000107",  # Severe acute respiratory syndrome coronavirus 2 immunisation course declined
]

e = clinical_events
event = (
    e.where(e.snomedct_code.is_in(codelist))
    .where(e.date.is_on_or_between(INTERVAL_START_DATE, INTERVAL_END_DATE))
    .sort_by(e.date)
    .first_for_patient()
)
had_matching_event = event.exists_for_patient()


# DATE RANGE
#
# The `Intervals` methods are helper functions which return a list of date pairs, being
# the start and ends (inclusive) of the specified intervals e.g.
#
#     Intervals.weeks_between("2020-01-01", "2020-01-15") == [
#         (date(2020,1,1), date(2020,1,7)),
#         (date(2020,1,8), date(2020,1,14)),
#         (date(2020,1,15), date(2020,1,21)),
#     ]
#
# `Intervals` is just acting as a namespace here; it felt cleaner to me to keep these
# together rather than having them as free floating functions. But I'm open to other
# suggestions.

intervals = Intervals.months_between("2020-12-01", "2021-04-01")


measures = [
    Measure(
        id="total",
        # Numerator can be any boolean or integer PatientSeries
        numerator=had_matching_event,
        # Denominator can also be any boolean or integer PatientSeries. The denominator
        # functions like `Dataset.define_population()` so only patients appearing in the
        # denominator can appear in the numerator.
        denominator=population,
        # I'm not wild about the use of `dict` here but I can't think of a better
        # syntactic solution.
        group_by=dict(
            age_band=age_band,
        ),
        # This can be any list of start/end date pairs – they don't have to be regular
        # or contiguous
        intervals=intervals,
    ),
    Measure(
        id="event_code",
        numerator=had_matching_event,
        # All these measures use the same denominator but they don't have to
        denominator=population,
        # The only restriction on `group_by` is that where multiple measures use the
        # same column name they must also share the same column definition. This allows
        # us to combine all the measures in a single output file, and I don't think is
        # too onerous a condition.
        group_by=dict(
            age_band=age_band,
            event_code=event.snomedct_code,
        ),
        # Likewise, all these measures use the same intervals, but they don't have to
        intervals=intervals,
    ),
    Measure(
        id="practice",
        numerator=had_matching_event,
        denominator=population,
        group_by=dict(
            age_band=age_band,
            practice=practice.practice_pseudo_id,
        ),
        intervals=intervals,
    ),
    Measure(
        id="practice",
        numerator=had_matching_event,
        denominator=population,
        group_by=dict(
            age_band=age_band,
            region=practice.nuts1_region_name,
        ),
        intervals=intervals,
    ),
]
