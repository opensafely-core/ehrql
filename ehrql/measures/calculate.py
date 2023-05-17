from collections import defaultdict

from ehrql.measures.measures import get_all_group_by_columns
from ehrql.query_model.nodes import Case, Function, Value, get_series_type
from ehrql.query_model.transforms import substitute_parameters


def get_measure_results(query_engine, measures):
    # Group measures by denominator and intervals as we'll handle them together
    grouped = defaultdict(list)
    for measure in measures:
        group_id = (measure.denominator, measure.intervals)
        grouped[group_id].append(measure)

    all_group_by_columns = get_all_group_by_columns(measures).keys()

    for measure_group in grouped.values():
        calculator = MeasureCalculator(measure_group)
        results = calculator.get_results(query_engine)
        for measure, interval, numerator, denominator, group_dict in results:
            ratio = numerator / denominator if denominator else None
            yield (
                measure.name,
                interval[0],
                interval[1],
                ratio,
                numerator,
                denominator,
                # Return a column for every group used across all measures, even if this
                # particular measure doesn't use that group
                *(group_dict.get(name) for name in all_group_by_columns),
            )


class MeasureCalculator:
    def __init__(self, measures):
        self.denominator = None
        self.intervals = None
        self.variables = {}
        self.measures = []
        self.fetchers = []
        for measure in measures:
            self.add_measure(measure)

    def get_results(self, query_engine):
        for interval in self.intervals:
            results = self.get_results_for_interval(query_engine, interval)
            for measure, numerator, denominator, group in results:
                group_dict = dict(zip(measure.group_by.keys(), group))
                yield measure, interval, numerator, denominator, group_dict

    def get_results_for_interval(self, query_engine, interval):
        # Build the query for this interval by replacing the interval start/end
        # placeholders with actual dates
        query = substitute_interval_parameters(self.variables, interval)

        # "fetchers" are functions which take a row and return the values relevant to a
        # given measure (numerator, denominator and groups); "accumulators" are dicts
        # storing the cumulative numerator and denominator totals for each group in the
        # measure
        fetcher_accumulator_pairs = [
            (fetcher, defaultdict(lambda: [0, 0])) for fetcher in self.fetchers
        ]

        for row in query_engine.get_results(query):
            for fetcher, accumulator in fetcher_accumulator_pairs:
                numerator, denominator, group = fetcher(row)
                totals = accumulator[group]
                totals[0] += numerator
                totals[1] += denominator

        for measure, (_, accumulator) in zip(self.measures, fetcher_accumulator_pairs):
            for group, (numerator, denominator) in accumulator.items():
                yield measure, numerator, denominator, group

    def add_measure(self, measure):
        # Record denominator and intervals from first measure
        if self.denominator is None:
            self.denominator = measure.denominator
            self.intervals = measure.intervals
            self.variables["population"] = series_as_bool(self.denominator)
        else:
            assert measure.denominator == self.denominator
            assert measure.intervals == self.intervals

        numerator_index = self.add_variable(series_as_int(measure.numerator))
        denominator_index = self.add_variable(series_as_int(measure.denominator))
        group_indexes = [
            self.add_variable(column) for column in measure.group_by.values()
        ]

        # Create a function which takes a results row and returns a numerator,
        # denominator, and tuple of group values, based on their indices
        fetcher = self.create_fetcher(numerator_index, denominator_index, group_indexes)

        self.measures.append(measure)
        self.fetchers.append(fetcher)

    def add_variable(self, variable):
        # Return the position of `variable` in the variables dict, adding it if not
        # already present
        try:
            return list(self.variables.values()).index(variable)
        except ValueError:
            index = len(self.variables)
            self.variables[f"column_{index}"] = variable
            return index

    @staticmethod
    def create_fetcher(numerator_index, denominator_index, group_indexes):
        # Given a bunch of indices we want a function which extracts just those indices
        # from a tuple. This is going to be called frequently, so the fastest way to do
        # this is to build a function definition and then eval it.
        group_items = [f"row[{i}]" for i in group_indexes]
        items = [
            f"row[{numerator_index}]",
            f"row[{denominator_index}]",
            f"({', '.join(group_items)},)",
        ]
        code = f"lambda row: ({', '.join(items)})"
        return eval(code)


def series_as_bool(series):
    series_type = get_series_type(series)
    if series_type is bool:
        return series
    elif series_type is int:
        return Function.GT(series, Value(0))
    else:
        assert False


def series_as_int(series):
    series_type = get_series_type(series)
    if series_type is int:
        return series
    elif series_type is bool:
        # TODO: This is definitely not the most efficient way to do this. We should
        # extend the `CastToInt` operation to apply to boolean as well.
        return Case(
            {
                Function.EQ(series, Value(True)): Value(1),
                Function.EQ(series, Value(False)): Value(0),
            }
        )
    else:
        assert False


def substitute_interval_parameters(variable_definitions, interval):
    return substitute_parameters(
        variable_definitions,
        interval_start_date=interval[0],
        interval_end_date=interval[1],
    )
