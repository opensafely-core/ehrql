from pathlib import Path

from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.nodes import get_table_nodes
from ehrql.utils.orm_utils import (
    orm_classes_from_tables,
    read_orm_models_from_csv_directory,
)


class CSVQueryEngine(InMemoryQueryEngine):
    """
    Subclass of the in-memory engine which loads its data from a directory of CSV files
    """

    def __init__(self, dsn, *args, **kwargs):
        # Treat the DSN as the path to a directory of CSVs
        self.csv_directory = dsn
        # The in-memory engine is a bit unusual in that it expects the DSN to be an
        # actual instance of the database
        dsn = InMemoryDatabase()
        super().__init__(dsn, *args, **kwargs)

    def get_results(self, variable_definitions):
        # Given the variables supplied determine the tables used and create
        # corresponding ORM classes
        table_nodes = get_table_nodes(*variable_definitions.values())
        self.populate_database(table_nodes)

        # Run the query as normal
        return super().get_results(variable_definitions)

    def evaluate(self, series_or_frame):
        table_nodes = get_table_nodes(series_or_frame.qm_node)
        self.populate_database(table_nodes)
        self.cache = {}
        return self.visit(series_or_frame.qm_node)

    def populate_database(self, table_nodes):
        # Populate the database using CSV files in the supplied directory
        orm_classes = orm_classes_from_tables(table_nodes)
        input_data = read_orm_models_from_csv_directory(
            Path(self.csv_directory), orm_classes.values()
        )
        self.database.setup(input_data)
