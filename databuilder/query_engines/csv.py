import csv
from pathlib import Path

import sqlalchemy
from sqlalchemy.orm import Session, declarative_base

from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_model import SelectPatientTable, SelectTable, all_nodes
from databuilder.sqlalchemy_types import Integer, type_from_python_type


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
        table_nodes = get_table_nodes(variable_definitions)
        orm_classes = create_orm_classes_from_table_nodes(table_nodes)
        assert orm_classes
        orm_classes[0].metadata.create_all(self.engine)

        # Populate the database using CSV files in the supplied directory
        input_data = read_all_csvs(self.csv_directory, orm_classes)
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


def create_orm_classes_from_table_nodes(table_nodes):
    Base = declarative_base()
    return [
        orm_class_from_schema(
            Base,
            node.name,
            node.schema,
        )
        for node in table_nodes
    ]


def orm_class_from_schema(base_class, table_name, schema):
    attributes = dict(
        __tablename__=table_name,
        # This column is only present because the SQLAlchemy ORM needs it
        _pk=sqlalchemy.Column(Integer, primary_key=True),
        patient_id=sqlalchemy.Column(Integer, nullable=False),
        **{
            col_name: sqlalchemy.Column(type_from_python_type(type_))
            for col_name, type_ in schema.items()
        },
    )
    return type(table_name, (base_class,), attributes)


def read_all_csvs(csv_directory, orm_classes):
    csv_directory = Path(csv_directory)
    for orm_class in orm_classes:
        csv_file = csv_directory / f"{orm_class.__tablename__}.csv"
        yield from orm_instances_from_csv(orm_class, csv_file)


def orm_instances_from_csv(orm_class, csv_file):
    fields = orm_class.__table__.columns.keys()
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield orm_class(**{k: v for k, v in row.items() if k in fields})
