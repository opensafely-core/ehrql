import datetime
import time
from collections import defaultdict
from dataclasses import dataclass

from ehrql.measures.measures import Measure, get_all_group_by_columns
from ehrql.query_model.column_specs import ColumnSpec, get_column_spec_from_series
from ehrql.query_model.nodes import (
    Dataset,
    Function,
    GroupedSum,
    Value,
    get_series_type,
)
from ehrql.query_model.transforms import substitute_parameters
from ehrql.utils.itertools_utils import iter_flatten
from ehrql.utils.math_utils import get_grouping_level_as_int
from ehrql.utils.sequence_utils import ordered_set


class MeasuresTimeout(Exception):
    pass


def get_measure_results(query_engine, measures, timeout=259200.0):
    # Group measures by denominator and intervals as we'll handle them together
    grouped = defaultdict(list)
    for measure in measures:
        group_id = (measure.denominator, measure.intervals)
        grouped[group_id].append(measure)
    all_group_by_columns = get_all_group_by_columns(measures).keys()

    measure_timer = MeasureTimer.from_grouped(timeout, grouped)
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
            measure_timer.check_timeout(interval)


def get_column_specs_for_measures(measures):
    return {
        "measure": ColumnSpec(
            str,
            categories=tuple(measure.name for measure in measures),
            nullable=False,
        ),
        "interval_start": ColumnSpec(datetime.date, nullable=False),
        "interval_end": ColumnSpec(datetime.date, nullable=False),
        "ratio": ColumnSpec(float),
        "numerator": ColumnSpec(int),
        "denominator": ColumnSpec(int),
        **{
            name: get_column_spec_from_series(column)
            for name, column in get_all_group_by_columns(measures).items()
        },
    }


class MeasureTimer:
    def __init__(self, timeout, num_iterations):
        self.timeout = timeout
        self.num_iterations = num_iterations
        self.previous_interval = None
        self.counter = 0

    @classmethod
    def from_grouped(cls, timeout, grouped):
        num_iterations = sum(
            [len(intervals) for denominator, intervals in grouped.keys()]
        )
        timer = MeasureTimer(timeout, num_iterations)
        timer.start()
        return timer

    def start(self):
        self.start_time = time.time()

    def check_timeout(self, interval):
        if interval != self.previous_interval:
            self.counter += 1
            self.previous_interval = interval
            if self.counter >= 12:
                self.elapsed_time = time.time() - self.start_time
                projected_time = self.elapsed_time / self.counter * self.num_iterations
                if projected_time > self.timeout:
                    raise MeasuresTimeout(
                        f"Generating measures exceeded {self.timeout}s time limit."
                    )


@dataclass
class MeasureFetcher:
    measure: Measure
    numerator_index: int
    grouping_level: int


class MeasureCalculator:
    def __init__(self, measures):
        self.denominator = None
        self.intervals = None
        self.population = None
        # column definitions from each measure, keyed in order defined
        # column_0 will always be the denominator
        self.variables = {}
        # lists of numerators, as the column keys in self.variables, in order
        self.numerator_keys = []
        # mapping of group by columns (a tuple of column keys) to numerator keys
        # If there are measures that share group by columns, they can be
        # handled together
        self.group_bys = {}
        # A list of MeasureFetcher instances, holding each measure, plus
        # additional information required for fetching results
        self.measure_fetchers = []

        # All group-by names from the measure definitions, in order (this is the
        # order that values will be returned in each results row)
        self.all_groups = ordered_set(iter_flatten(list(m.group_by) for m in measures))

        for measure in measures:
            self.add_measure(measure)

        grouped_sum = GroupedSum(
            numerators=tuple(self.numerator_keys),
            denominator=list(self.variables.keys())[0],
            group_bys={k: tuple(v) for k, v in self.group_bys.items()},
        )

        self.placeholder_dataset = Dataset(
            population=self.population,
            variables=self.variables,
            events={},
            measures=grouped_sum,
        )

    def get_results(self, query_engine):
        for interval in self.intervals:
            results = self.get_results_for_interval(query_engine, interval)

            for measure, numerator, denominator, *groups in results:
                group_dict = dict(zip(self.all_groups, groups))
                yield measure, interval, numerator, denominator, group_dict

    def get_results_for_interval(self, query_engine, interval):
        # Build the query for this interval by replacing the interval start/end
        # placeholders with actual dates
        dataset = substitute_interval_parameters(self.placeholder_dataset, interval)
        groups_count = len(self.all_groups)

        for table in query_engine.get_results_tables(dataset):
            for row in table:
                # Each row contains values in the order:
                # [denominator, *all_numerators, *all_group_by_columns, grouping_id]
                denominator = row[0]
                grouping_level = row[-1]
                row = row[1:-1]

                for fetcher in self.measure_fetchers:
                    # To determine which measure(s) this row applies to, we look at its
                    # grouping level which is a numeric representation of the subset of
                    # all group_bys that are applied to this measure
                    # If its level matches the row's grouping level, values for this measure
                    # should be extracted from the row
                    if fetcher.grouping_level != grouping_level:
                        continue
                    # Extract the numerator for this measure
                    numerator = row[fetcher.numerator_index]
                    yield (
                        fetcher.measure,
                        numerator,
                        denominator,
                        *row[(len(row) - groups_count) :],
                    )

    def add_measure(self, measure):
        # Record denominator and intervals from first measure
        if self.denominator is None:
            self.denominator = measure.denominator
            self.intervals = measure.intervals
            self.population = series_as_bool(self.denominator)
            assert not self.variables
            self.add_variable(series_as_int(measure.denominator))
        else:
            assert measure.denominator == self.denominator
            assert measure.intervals == self.intervals

        numerator_key = self.add_variable(series_as_int(measure.numerator))
        if numerator_key not in self.numerator_keys:
            self.numerator_keys.append(numerator_key)
        group_keys = tuple(
            [self.add_variable(column) for column in measure.group_by.values()]
        )
        self.group_bys.setdefault(group_keys, set()).add(numerator_key)

        self.measure_fetchers.append(
            MeasureFetcher(
                measure=measure,
                numerator_index=self.numerator_keys.index(numerator_key),
                grouping_level=get_grouping_level_as_int(
                    self.all_groups, measure.group_by
                ),
            )
        )

    def add_variable(self, variable):
        # Return the name for `variable` in the variables dict, adding it if not
        # already present
        try:
            return next(k for k, v in self.variables.items() if v == variable)
        except StopIteration:
            index = len(self.variables)
            key = f"column_{index}"
            self.variables[key] = variable
            return key


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
        return Function.CastToInt(series)
    else:
        assert False


def substitute_interval_parameters(dataset, interval):
    return substitute_parameters(
        dataset,
        interval_start_date=interval[0],
        interval_end_date=interval[1],
    )
