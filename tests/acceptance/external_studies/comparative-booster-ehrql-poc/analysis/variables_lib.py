import operator
from functools import reduce

from databuilder.codes import CTV3Code, ICD10Code
from databuilder.ehrql import case, days, when
from databuilder.tables.beta import tpp as schema


def any_of(conditions):
    return reduce(operator.or_, conditions)


def create_sequential_variables(
    dataset, variable_name_template, events, column, num_variables, sort_column=None
):
    sort_column = sort_column or column
    for index in range(num_variables):
        next_event = events.sort_by(getattr(events, sort_column)).first_for_patient()
        events = events.where(
            getattr(events, sort_column) > getattr(next_event, sort_column)
        )
        variable_name = variable_name_template.format(n=index + 1)
        setattr(dataset, variable_name, getattr(next_event, column))


def _registrations_overlapping_period(start_date, end_date):
    regs = schema.practice_registrations
    return regs.where(
        regs.start_date.is_on_or_before(start_date)
        & (regs.end_date.is_after(end_date) | regs.end_date.is_null())
    )


def practice_registration_as_of(date):
    regs = _registrations_overlapping_period(date, date)
    return regs.sort_by(regs.start_date, regs.end_date).first_for_patient()


def age_as_of(date):
    return (date - schema.patients.date_of_birth).years


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
    active = addr.where(
        addr.start_date.is_on_or_before(date)
        & (addr.end_date.is_after(date) | addr.end_date.is_null())
    )
    # Where there are multiple active address registrations we need to pick one.
    # Logic copied from:
    # https://github.com/opensafely-core/cohort-extractor/blob/e77a0aa2/cohortextractor/tpp_backend.py#L1756-L1773
    ordered = active.sort_by(
        # Prefer the most recently registered address
        addr.start_date,
        # Prefer the address registered for longest
        addr.end_date,
        # Prefer addresses with a postcode
        case(when(addr.has_postcode).then(1), default=0),
        # Use the opaque ID as a tie-breaker for sort stability (we invert this simply
        # so the order matches the original order defined in Cohort Extractor to
        # facilitate direct comparison)
        -addr.address_id,
    )
    return ordered.last_for_patient()


def most_recent_bmi(*, minimum_age_at_measurement, where=True):
    events = schema.clinical_events
    age_threshold = schema.patients.date_of_birth + days(
        # This is obviously inexact but, given that the dates of birth are rounded to
        # the first of the month anyway, there's no point trying to be more accurate
        int(365.25 * minimum_age_at_measurement)
    )
    return (
        # This captures just explicitly recorded BMI observations rather than attempting
        # to calculate it from height and weight measurements. Investigation has shown
        # this to have no real benefit it terms of coverage or accuracy.
        events.where(events.ctv3_code == CTV3Code("22K.."))
        .where(events.date >= age_threshold)
        .where(where)
        .sort_by(events.date)
        .last_for_patient()
    )


def emergency_care_diagnosis_matches(emergency_care_attendances, codelist):
    conditions = [
        getattr(emergency_care_attendances, column_name).is_in(codelist)
        for column_name in [f"diagnosis_{i:02d}" for i in range(1, 25)]
    ]
    return emergency_care_attendances.where(any_of(conditions))


def hospitalisation_diagnosis_matches(admissions, codelist):
    code_strings = set()
    for code in codelist:
        # Pass the string through the ICD10Code to constructor to validate that it has
        # the expected format
        code_string = ICD10Code(code)._to_primitive_type()
        code_strings.add(code_string)
    conditions = [
        # The reason a plain substring search like this works is twofold:
        #
        # * ICD-10 codes all start with the sequence [A-Z][0-9] and do not contain
        #   such a sequence in any other part of the code. In this sense they are
        #   suffix-free and two codes will only match at they start if they match at
        #   all.
        #
        # * Although the codes are not prefix-free they are organised hierarchically
        #   such that code A0123 represents a child concept of code A01. So although
        #   the naive substring matching below will find code A01 if code A0123 is
        #   present, this happens to be the behaviour we actually want.
        #
        # Obviously this is all far from ideal though, and later we hope to be able
        # to pull these codes out in a separate table and handle the matching
        # properly.
        admissions.all_diagnoses.contains(code_str)
        for code_str in code_strings
    ]
    return admissions.where(any_of(conditions))
