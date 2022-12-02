import contextlib
import os
import pprint
from collections import defaultdict

import pytest

from databuilder.query_model.nodes import count_nodes, node_types

from . import variable_strategies


class ObservedInputs:
    _inputs = set()

    def record(self, variable, data):
        hashable_data = frozenset(self._hashable(item) for item in data)
        self._inputs.add((variable, hashable_data))

    @property
    def variables(self):  # pragma: no cover
        return {i[0] for i in self._inputs}

    @property
    def records(self):  # pragma: no cover
        return {i[1] for i in self._inputs}

    @property
    def unique_inputs(self):  # pragma: no cover
        return self._inputs

    @staticmethod
    def _hashable(item):
        copy = item.copy()

        # SQLAlchemy ORM objects aren't hashable, but the name is good enough for us
        copy["type"] = copy["type"].__name__

        # There are only a small number of values in each record and their order is predictable,
        # so we can record just the values as a tuple and recover the field names later
        # if we want them.
        return tuple(copy.values())


@pytest.fixture(scope="session")
def recorder(request):  # pragma: no cover
    observed_inputs = ObservedInputs()

    yield observed_inputs.record

    if "GENTEST_COMPREHENSIVE" in os.environ:
        check_comprehensive(observed_inputs)

    if "GENTEST_DEBUG" in os.environ:
        with output_enabled(request):
            show_input_summary(observed_inputs)


def check_comprehensive(observed_inputs):  # pragma: no cover
    operations_seen = {o for v in observed_inputs.variables for o in node_types(v)}
    variable_strategies.assert_includes_all_operations(operations_seen)


def show_input_summary(observed_inputs):  # pragma: no cover
    print()
    print(f"\n{len(observed_inputs.unique_inputs)} unique input combinations")
    show_variables_summary(observed_inputs)
    show_records_summary(observed_inputs)


def show_variables_summary(observed_inputs):  # pragma: no cover
    observed_variables = observed_inputs.variables
    print(f"\n{len(observed_variables)} unique queries")
    counts = [count_nodes(example) for example in observed_variables]
    count_histo = histogram(counts)
    print("\nwith this node count distribution")
    for count, num in count_histo:
        print(f"{count:3}\t{num}")
    if observed_variables:
        print("\nlargest query")
        by_size = sorted(observed_variables, key=lambda v: count_nodes(v))
        pprint.pprint(by_size[-1])
    all_node_types = [
        type_.__name__
        for variable in observed_variables
        for type_ in node_types(variable)
    ]
    type_histo = histogram(all_node_types)
    print("\nand these node types")
    for type_, num in sorted(type_histo, key=lambda item: item[1], reverse=True):
        print(f"{type_:25}{num}")


def show_records_summary(observed_inputs):  # pragma: no cover
    observed_records = observed_inputs.records
    print(f"\n{len(observed_records)} unique datasets")
    record_counts = [len(records) for records in observed_records]
    record_count_histo = histogram(record_counts)
    print("\nwith this size distribution")
    for count, num in record_count_histo:
        print(f"{count:3}\t{num}")


def histogram(samples):  # pragma: no cover
    h = defaultdict(int)
    for sample in samples:
        h[sample] = h[sample] + 1
    return sorted(h.items())


@contextlib.contextmanager
def output_enabled(request):  # pragma: no cover
    capturemanager = request.config.pluginmanager.getplugin("capturemanager")
    with capturemanager.global_and_fixture_disabled():
        yield
