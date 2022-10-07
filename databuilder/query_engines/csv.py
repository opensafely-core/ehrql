from pathlib import Path

from databuilder.orm_utils import (
    orm_classes_from_qm_tables,
    read_orm_models_from_csv_directory,
)
from databuilder.query_engines.in_memory import InMemoryQueryEngine
from databuilder.query_engines.in_memory_database import InMemoryDatabase
from databuilder.query_model import get_table_nodes


class CSVQueryEngine(InMemoryQueryEngine):
    """
    Subclass of the in-memory engine which loads its data from a directory of CSV files
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Treat the DSN as the path to a directory of CSVs
        self.csv_directory = self.dsn
        # This gives us an in memory SQLite database
        self.dsn = InMemoryDatabase()

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
