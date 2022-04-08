import os
import pprint
from collections import defaultdict

from databuilder.query_model import count_nodes, node_types

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


def histogram(samples):  # pragma: no cover
    h = defaultdict(int)
    for sample in samples:
        h[sample] = h[sample] + 1
    return sorted(h.items())


def pytest_terminal_summary(terminalreporter, exitstatus, config):  # pragma: no cover
    if "DEBUG" not in os.environ:
        return

    print(f"\n{len(observed_inputs)} unique input combinations")

    observed_variables = {i[0] for i in observed_inputs}
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

    observed_records = {i[1] for i in observed_inputs}
    print(f"\n{len(observed_records)} unique datasets")

    record_counts = [len(records) for records in observed_records]
    record_count_histo = histogram(record_counts)
    print("\nwith this size distribution")
    for count, num in record_count_histo:
        print(f"{count:3}\t{num}")
