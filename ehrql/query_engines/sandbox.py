from functools import reduce

from ehrql.query_engines.local_file import LocalFileQueryEngine
from ehrql.query_language import compile
from ehrql.query_model.introspection import get_table_nodes
from ehrql.query_model.nodes import AggregateByPatient, Function


class SandboxQueryEngine(LocalFileQueryEngine):
    def evaluate_dataset(self, dataset_definition):
        variable_definitions = compile(dataset_definition)
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

    def evaluate(self, series_or_frame):
        table_nodes = get_table_nodes(series_or_frame._qm_node)
        self.populate_database(table_nodes)
        self.cache = {}
        return self.visit(series_or_frame._qm_node)


class EmptyDataset:
    """This class exists to render something nice when a user tries to inspect a dataset
    with no columns in the sandbox."""

    def _render_(self, render_fn):
        return render_fn([{"patient_id": ""}])
