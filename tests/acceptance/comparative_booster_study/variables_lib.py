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
