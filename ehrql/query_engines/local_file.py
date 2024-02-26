from pathlib import Path

from ehrql.file_formats import read_tables
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.column_specs import get_column_specs_from_schema
from ehrql.query_model.introspection import get_table_nodes
from ehrql.utils.orm_utils import orm_classes_from_tables


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
        # Given the variables supplied determine the tables used and create
        # corresponding ORM classes
        table_nodes = get_table_nodes(*variable_definitions.values())
        self.populate_database(table_nodes)

        # Run the query as normal
        return super().get_results(variable_definitions)

    def populate_database(self, table_nodes):
        # Populate the database using the files in the supplied directory
        self.database.setup(self.get_input_data(table_nodes))

    def get_input_data(self, table_nodes):
        table_specs = {
            table.name: get_column_specs_from_schema(table.schema)
            for table in table_nodes
        }
        tables = read_tables(
            self.data_directory,
            table_specs,
            allow_missing_columns=True,
        )
        orm_classes = orm_classes_from_tables(table_nodes)
        for (table_name, columns), rows in zip(table_specs.items(), tables):
            orm_class = orm_classes[table_name]
            for row in rows:
                yield orm_class(**dict(zip(columns, row)))
