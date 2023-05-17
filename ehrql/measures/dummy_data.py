from functools import reduce

from ehrql.dummy_data import DummyDataGenerator
from ehrql.measures.calculate import (
    get_all_group_by_columns,
    get_measure_results,
    series_as_bool,
    substitute_interval_parameters,
)
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.nodes import Function


class DummyMeasuresDataGenerator:
    def __init__(self, measures):
        self.measures = measures
        variables, population_size = self._variables_and_population_size(measures)
        self.generator = DummyDataGenerator(variables, population_size=population_size)

    def _variables_and_population_size(self, measures):
        # Collect all variables used in all measures
        all_denominators = {series_as_bool(m.denominator) for m in measures}
        all_numerators = {m.numerator for m in measures}
        all_groups = get_all_group_by_columns(measures).values()

        variable_placeholders = {
            # Use the union of all denominators as the population
            "population": reduce(Function.Or, all_denominators),
            **{
                f"column_{i}": column
                for i, column in enumerate([*all_numerators, *all_groups])
            },
        }

        # Use the maximum range over all intervals as a date range
        all_intervals = {interval for m in measures for interval in m.intervals}
        min_interval_start = min(interval[0] for interval in all_intervals)
        max_interval_end = max(interval[1] for interval in all_intervals)

        variables = substitute_interval_parameters(
            variable_placeholders, (min_interval_start, max_interval_end)
        )

        # Totally unscientific heuristic for producing a "big enough" population to
        # generate a "reasonable" amount of non-zero measures
        population_size = (
            10 * len(all_denominators) * len(all_intervals) * len(all_groups)
        )

        return variables, population_size

    def get_data(self):
        return self.generator.get_data()

    def get_results(self):
        database = InMemoryDatabase()
        database.setup(self.get_data())
        engine = InMemoryQueryEngine(database)
        return get_measure_results(engine, self.measures)
