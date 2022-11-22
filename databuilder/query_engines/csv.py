from pathlib import Path

from databuilder.query_engines.in_memory import InMemoryQueryEngine
from databuilder.query_engines.in_memory_database import InMemoryDatabase
from databuilder.query_model.nodes import get_table_nodes
from databuilder.utils.orm_utils import (
    orm_classes_from_qm_tables,
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
        orm_classes = orm_classes_from_qm_tables(table_nodes)
        # Populate the database using CSV files in the supplied directory
        input_data = read_orm_models_from_csv_directory(
            Path(self.csv_directory), orm_classes
        )
        self.dsn.setup(input_data)

        # Run the query as normal
        return super().get_results(variable_definitions)
