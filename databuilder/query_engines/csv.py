import csv
from pathlib import Path

from sqlalchemy.orm import Session, declarative_base

from databuilder.orm_factory import orm_class_from_qm_table
from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_model import SelectPatientTable, SelectTable, all_nodes


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
        # This flag creates empty "template" CSV files with the appropriate headers for
        # any missing files
        self.create_missing = bool(self.config.get("DATABUILDER_CREATE_MISSING_CSV"))

    def get_results(self, variable_definitions):
        # Given the variables supplied determine the tables used, create corresponding
        # ORM classes and use them to initialise the database schema
        table_nodes = get_table_nodes(variable_definitions)
        Base = declarative_base()
        orm_classes = [orm_class_from_qm_table(Base, node) for node in table_nodes]
        assert orm_classes
        orm_classes[0].metadata.create_all(self.engine)

        # Populate the database using CSV files in the supplied directory
        input_data = read_all_csvs(
            self.csv_directory, orm_classes, create_missing=self.create_missing
        )
        with Session(self.engine) as session:
            session.bulk_save_objects(input_data)
            session.commit()

        # Run the query as normal
        return super().get_results(variable_definitions)


def get_table_nodes(variables):
    table_nodes = set()
    for variable in variables.values():
        for node in all_nodes(variable):
            if isinstance(node, (SelectTable, SelectPatientTable)):
                table_nodes.add(node)
    return table_nodes


def read_all_csvs(csv_directory, orm_classes, create_missing=False):
    csv_directory = Path(csv_directory)
    for orm_class in orm_classes:
        csv_file = csv_directory / f"{orm_class.__tablename__}.csv"
        yield from orm_instances_from_csv(orm_class, csv_file, create_missing)


def orm_instances_from_csv(orm_class, csv_file, create_missing=False):
    fields = orm_class.__table__.columns.keys()
    if create_missing and not csv_file.exists():
        csv_file.write_text(",".join(f for f in fields if f != "_pk") + "\n")
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield orm_class(**{k: v for k, v in row.items() if k in fields})
