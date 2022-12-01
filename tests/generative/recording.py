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


observed_inputs = ObservedInputs()


@pytest.fixture(scope="session")
def recorder():  # pragma: no cover
    yield observed_inputs.record

    if not os.getenv("GENTEST_COMPREHENSIVE"):
        return

    operations_seen = {o for v in observed_inputs.variables for o in node_types(v)}
    variable_strategies.assert_includes_all_operations(operations_seen)


def histogram(samples):  # pragma: no cover
    h = defaultdict(int)
    for sample in samples:
        h[sample] = h[sample] + 1
    return sorted(h.items())


def show_input_summary():  # pragma: no cover
    if "GENTEST_DEBUG" not in os.environ:
        return

    print(f"\n{len(observed_inputs.unique_inputs)} unique input combinations")

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

    observed_records = observed_inputs.records
    print(f"\n{len(observed_records)} unique datasets")

    record_counts = [len(records) for records in observed_records]
    record_count_histo = histogram(record_counts)
    print("\nwith this size distribution")
    for count, num in record_count_histo:
        print(f"{count:3}\t{num}")
