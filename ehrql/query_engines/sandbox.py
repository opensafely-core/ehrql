from functools import reduce

from ehrql.query_engines.in_memory_database import apply_function
from ehrql.query_engines.local_file import LocalFileQueryEngine
from ehrql.query_language import Dataset, DateDifference
from ehrql.query_model.introspection import get_table_nodes
from ehrql.query_model.nodes import AggregateByPatient, Function


class SandboxQueryEngine(LocalFileQueryEngine):
    def evaluate_dataset(self, dataset_definition):
        variable_definitions = dataset_definition._compile()
        if not variable_definitions:
            return EmptyDataset()
        table_nodes = get_table_nodes(*variable_definitions.values())
        if "population" not in variable_definitions:
            # When the dataset does not have a defined population, we include all
            # patients with a value in any of the tables used in the query.
            variable_definitions["population"] = reduce(
                Function.Or,
                map(AggregateByPatient.Exists, table_nodes),
            )
        self.populate_database(table_nodes)
        return self.get_results_as_table(variable_definitions)

    def evaluate(self, element):
        if isinstance(element, Dataset):
            return self.evaluate_dataset(element)

        original_element = element
        element = (
            element.days if isinstance(original_element, DateDifference) else element
        )

        table_nodes = get_table_nodes(element._qm_node)
        self.populate_database(table_nodes)
        self.cache = {}
        column = self.visit(element._qm_node)

        if isinstance(original_element, DateDifference):
            column = apply_function(format_date_difference, column)
        return column


def format_date_difference(obj):
    if obj is None:
        return obj
    return f"{obj} days"


class EmptyDataset:
    """This class exists to render something nice when a user tries to inspect a dataset
    with no columns in the sandbox."""

    def _render_(self, render_fn):
        return render_fn([{"patient_id": ""}])
