import itertools
import os
from collections import defaultdict

from databuilder.query_model import get_input_nodes

observed_inputs = set()


def observe_inputs(variable, records):
    def hashify(record):
        record = record.copy()

        # SQLAlchemy ORM objects aren't hashable, but the name is good enough for us
        record["type"] = record["type"].__name__

        # There are only a small number of values in each record and their order is predictable, so we can record just
        # the values as a tuple and recover the field names later if we want them
        return tuple(record.values())

    hashable_data = frozenset(hashify(record) for record in records)

    observed_inputs.add((variable, hashable_data))


def count_nodes(tree):  # pragma: no cover
    return 1 + sum(count_nodes(node) for node in get_input_nodes(tree))


def node_types(tree):  # pragma: no cover
    return [type(tree)] + flatten(node_types(node) for node in get_input_nodes(tree))


def flatten(lists):  # pragma: no cover
    return list(itertools.chain.from_iterable(lists))


def histogram(samples):  # pragma: no cover
    h = defaultdict(int)
    for sample in samples:
        h[sample] = h[sample] + 1
    return dict(h.items())


def pytest_terminal_summary(terminalreporter, exitstatus, config):  # pragma: no cover
    if "DEBUG" not in os.environ:
        return

    print(f"\n{len(observed_inputs)} unique inputs")

    observed_variables = {i[0] for i in observed_inputs}

    counts = [count_nodes(example) for example in observed_variables]
    count_histo = histogram(counts)
    print(f"\n{len(observed_variables)} unique examples with node count distribution:")
    for count, num in sorted(count_histo.items(), key=lambda item: item[0]):
        print(f"{count:3}\t{num}")

    types = flatten(node_types(example) for example in observed_variables)
    type_histo = histogram(types)
    print("\nNode types:")
    for type_, num in sorted(
        type_histo.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"{type_.__name__:25}{num}")

    observed_records = {i[1] for i in observed_inputs}

    record_counts = [len(records) for records in observed_records]
    record_count_histo = histogram(record_counts)
    print(f"\n{len(observed_records)} unique datasets with size distribution")
    for count, num in sorted(record_count_histo.items(), key=lambda item: item[0]):
        print(f"{count:3}\t{num}")
