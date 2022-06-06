def create_sequential_variables(
    dataset, variable_name_template, events, column, num_variables
):
    next_events = events
    for index in range(num_variables):
        variable_def = getattr(next_events, column).minimum_for_patient()
        next_events = events.take(getattr(events, column) > variable_def)
        variable_name = variable_name_template.format(n=index + 1)
        setattr(dataset, variable_name, variable_def)
