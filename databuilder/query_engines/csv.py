from pathlib import Path

from sqlalchemy.orm import Session

from databuilder.orm_utils import (
    orm_classes_from_qm_tables,
    read_orm_models_from_csv_directory,
)
from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_model import get_table_nodes


class CSVQueryEngine(SQLiteQueryEngine):
    """
    This is a subclass of the SQLite engine which loads its data from a supplied
    directory of CSV files. It exists purely for demonstration purposes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Treat the DSN as the path to a directory of CSVs
        self.csv_directory = self.dsn
        # This gives us an in memory SQLite database
        self.dsn = "sqlite://"

    def get_results(self, variable_definitions):
        # Given the variables supplied determine the tables used, create corresponding
        # ORM classes and use them to initialise the database schema
        table_nodes = get_table_nodes(*variable_definitions.values())
        orm_classes = orm_classes_from_qm_tables(table_nodes)
        assert orm_classes
        orm_classes[0].metadata.create_all(self.engine)

        # Populate the database using CSV files in the supplied directory
        input_data = read_orm_models_from_csv_directory(
            Path(self.csv_directory), orm_classes
        )
        with Session(self.engine) as session:
            session.bulk_save_objects(input_data)
            session.commit()

        # Run the query as normal
        return super().get_results(variable_definitions)
