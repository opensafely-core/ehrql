from pathlib import Path

from ehrql.file_formats import read_tables
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.column_specs import get_column_specs_from_schema
from ehrql.query_model.introspection import get_table_nodes


class LocalFileQueryEngine(InMemoryQueryEngine):
    """
    Subclass of the in-memory engine which loads its data from files
    """

    def __init__(self, dsn, *args, **kwargs):
        # Treat the DSN as the path to a directory of table files
        self.data_directory = Path(dsn)
        # The in-memory engine is a bit unusual in that it expects the DSN to be an
        # actual instance of the database
        dsn = InMemoryDatabase()
        super().__init__(dsn, *args, **kwargs)

    def get_results(self, variable_definitions):
        # Given the variables supplied determine the tables used and load the associated
        # data into the database
        table_nodes = get_table_nodes(*variable_definitions.values())
        self.populate_database(table_nodes)

        # Run the query as normal
        return super().get_results(variable_definitions)

    def populate_database(self, table_nodes):
        # Populate the database using the files in the supplied directory
        table_specs = {
            table.name: get_column_specs_from_schema(table.schema)
            for table in table_nodes
        }
        table_rows = read_tables(
            self.data_directory,
            table_specs,
            allow_missing_columns=True,
        )
        table_data = dict(zip(table_nodes, table_rows))
        self.database.populate(table_data)
