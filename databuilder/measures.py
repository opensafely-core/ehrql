from collections import defaultdict


def get_sum_group_by(
    query_engine, population_definition, variables_to_sum, variables_to_group_by
):
    variables = {"population": population_definition}
    for n, variable in enumerate(variables_to_sum, start=1):
        variables[f"value_{n}"] = variable
    for n, variable in enumerate(variables_to_group_by, start=1):
        variables[f"group_{n}"] = variable

    value_indexes = slice(1, len(variables_to_sum) + 1)
    group_indexes = slice(1 + len(variables_to_sum), None)
    empty_values = (0,) * len(variables_to_sum)
    sums = defaultdict(lambda: empty_values)

    for row in query_engine.get_results(variables):
        values = row[value_indexes]
        group = row[group_indexes]
        sums[group] = [
            (i + j) if j is not None else i for i, j in zip(sums[group], values)
        ]

    return [(*values, *group) for group, values in sums.items()]


class GroupedSum:

    def __init__(self, *, population, values, group_by, date_start, date_end, frequency):
        self.population = population
        self.values = values
        self.group_by = group_by
        self.date_start = date_start
        self.date_end = date_end
        self.frequency = frequency
