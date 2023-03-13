import operator
from functools import reduce

from databuilder.codes import ICD10Code
from databuilder.ehrql import case, when
from databuilder.tables.beta import tpp as schema


def has_matching_event(events, codelist, where=True):
    return (
        events.where(where)
        .where(events.snomedct_code.is_in(codelist))
        .exists_for_patient()
    )


def any_of(conditions):
    return reduce(operator.or_, conditions)


def age_as_of(date):
    return (date - schema.patients.date_of_birth).years


# TODO this is not exactly the same as died_from_any_cause().
# Note that this function only checks the patient table
def died_as_of(date):
    return schema.patients.date_of_death.is_not_null() & (
        schema.patients.date_of_death < date
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


def _registrations_overlapping_period(start_date, end_date):
    regs = schema.practice_registrations
    return regs.where(
        regs.start_date.is_on_or_before(start_date)
        & (regs.end_date.is_after(end_date) | regs.end_date.is_null())
    )


def practice_registration_as_of(date):
    regs = _registrations_overlapping_period(date, date)
    return regs.sort_by(regs.start_date, regs.end_date).first_for_patient()


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
        admissions.all_diagnoses.contains(code_string)
        for code_string in code_strings
    ]
    return admissions.where(any_of(conditions))
