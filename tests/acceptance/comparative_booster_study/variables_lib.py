from databuilder.query_language import case, when

from . import schema


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
