import operator
from functools import reduce

from databuilder.codes import CTV3Code
from databuilder.query_language import case, when

from . import schema


def any_of(conditions):
    return reduce(operator.or_, conditions)


def create_sequential_variables(
    dataset, variable_name_template, events, column, num_variables
):
    next_events = events
    for index in range(num_variables):
        variable_def = getattr(next_events, column).minimum_for_patient()
        next_events = events.take(getattr(events, column) > variable_def)
        variable_name = variable_name_template.format(n=index + 1)
        setattr(dataset, variable_name, variable_def)


def _registrations_overlapping_period(start_date, end_date):
    regs = schema.practice_registrations
    return regs.take(
        regs.start_date.is_on_or_before(start_date)
        & (regs.end_date.is_after(end_date) | regs.end_date.is_null())
    )


def practice_registration_as_of(date):
    regs = _registrations_overlapping_period(date, date)
    return regs.sort_by(regs.start_date, regs.end_date).first_for_patient()


def age_as_of(date):
    return schema.patients.date_of_birth.difference_in_years(date)


def has_a_continuous_practice_registration_spanning(start_date, end_date):
    return _registrations_overlapping_period(start_date, end_date).exists_for_patient()


def date_deregistered_from_all_supported_practices():
    max_dereg_date = schema.practice_registrations.end_date.maximum_for_patient()
    # In TPP currently active registrations are recorded as having an end date of
    # 9999-12-31. We convert these, and any other far-future dates, to NULL.
    return case(
        when(max_dereg_date.is_before("3000-01-01")).then(max_dereg_date),
        default=None,
    )


def address_as_of(date):
    addr = schema.addresses
    active = addr.take(
        addr.start_date.is_on_or_before(date)
        & (addr.end_date.is_after(date) | addr.end_date.is_null())
    )
    # Where there are multiple active address registrations we need to pick one.
    # Logic copied from:
    # https://github.com/opensafely-core/cohort-extractor/blob/e77a0aa2/cohortextractor/tpp_backend.py#L1756-L1773
    ordered = active.sort_by(
        # Prefer the address which was registered first
        addr.start_date,
        # Prefer the address registered for longest
        addr.end_date,
        # Prefer those which aren't classified as "NPC" (No Postcode)
        case(when(addr.msoa_code == "NPC").then(1), default=0),
        # Use the opaque ID as a tie-breaker for sort stability
        addr.address_id,
    )
    return ordered.first_for_patient()


def most_recent_bmi(*, minimum_age_at_measurement, where=True):
    events = schema.coded_events
    age_threshold = schema.patients.date_of_birth.add_days(
        # This is obviously inexact but, given that the dates of birth are rounded to
        # the first of the month anyway, there's no point trying to be more accurate
        int(365.25 * minimum_age_at_measurement)
    )
    return (
        # This captures just explicitly recorded BMI observations rather than attempting
        # to calculate it from height and weight measurements. Investigation has shown
        # this to have no real benefit it terms of coverage or accuracy.
        events.take(events.ctv3_code == CTV3Code("22K.."))
        .take(events.date >= age_threshold)
        .take(where)
        .sort_by(events.date)
        .last_for_patient()
    )


def cause_of_death_matches(deaths, codelist):
    conditions = [
        getattr(deaths, column_name).is_in(codelist)
        for column_name in [f"cause_of_death_{i:02d}" for i in range(1, 16)]
    ]
    return deaths.take(any_of(conditions))


def emergency_care_diagnosis_matches(emergency_care_attendances, codelist):
    conditions = [
        getattr(emergency_care_attendances, column_name).is_in(codelist)
        for column_name in [f"diagnosis_{i:02d}" for i in range(1, 25)]
    ]
    return emergency_care_attendances.take(any_of(conditions))
