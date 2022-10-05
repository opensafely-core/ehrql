import csv
from types import SimpleNamespace

import sqlalchemy
from sqlalchemy.orm import declarative_base

from databuilder.query_language import BaseFrame
from databuilder.query_model import has_one_row_per_patient
from databuilder.sqlalchemy_types import Integer, type_from_python_type

# Generate an integer sequence to use as default IDs. Normally you'd rely on the DBMS to
# provide these, but we need to support DBMSs like Spark which don't have this feature.
next_id = iter(range(1, 2**63)).__next__


# We need each NULL-able column to have an explicit default of NULL. Without this,
# SQLAlchemy will just omit empty columns from the INSERT. That's fine for most DBMSs
# but Spark needs every column in the table to be specified, even if it just has a NULL
# value. Note: we have to use a callable returning `None` here because if we use `None`
# directly SQLAlchemy interprets this is "there is no default".
def null():
    return None


def orm_class_from_schema(base_class, table_name, schema, has_one_row_per_patient):
    """
    Given a SQLAlchemy ORM "declarative base" class, a table name and a schema, return
    an ORM class with the schema of that table
    """
    attributes = {"__tablename__": table_name}

    if has_one_row_per_patient:
        attributes["patient_id"] = sqlalchemy.Column(Integer, primary_key=True)
    else:
        attributes["patient_id"] = sqlalchemy.Column(Integer, nullable=False)
        attributes["row_id"] = sqlalchemy.Column(
            Integer, primary_key=True, default=next_id
        )

    for col_name, type_ in schema.column_types:
        attributes[col_name] = sqlalchemy.Column(
            type_from_python_type(type_), default=null
        )

    class_name = table_name.title().replace("_", "")

    return type(class_name, (base_class,), attributes)


def orm_class_from_qm_table(base_class, qm_table):
    """
    Given a SQLAlchemy ORM "declarative base" class and a QM table, return an ORM
    class with the schema of that table
    """
    return orm_class_from_schema(
        base_class, qm_table.name, qm_table.schema, has_one_row_per_patient(qm_table)
    )


def orm_class_from_ql_table(base_class, table):
    """
    Given a SQLAlchemy ORM "declarative base" class and a QL table, return an ORM
    class with the schema of that table
    """
    return orm_class_from_qm_table(base_class, table.qm_node)


def orm_classes_from_ql_table_namespace(namespace):
    """
    Given a namespace containing QL tables, return a namespace where each QL table is
    mapped to an equivalent ORM class
    """
    Base = declarative_base()
    orm_classes = {"Base": Base}
    for attr, value in vars(namespace).items():
        if isinstance(value, BaseFrame):
            orm_classes[attr] = orm_class_from_ql_table(Base, value)
    return SimpleNamespace(**orm_classes)


def orm_classes_from_qm_tables(qm_tables):
    """
    Given a list of Query Model tables, return a list of corresponding ORM instances
    """
    Base = declarative_base()
    return [orm_class_from_qm_table(Base, table) for table in qm_tables]


def table_has_one_row_per_patient(table):
    """Given a SQLAlchemy ORM table, return boolean indicating whether the table has one
    row per patient."""
    return table.columns["patient_id"].primary_key


def read_orm_models_from_csv_directory(directory, orm_classes):
    for orm_class in orm_classes:
        csv_file = directory / f"{orm_class.__tablename__}.csv"
        with open(csv_file, newline="") as fileobj:
            yield from read_orm_models_from_csv_lines(fileobj, orm_class)


def read_orm_models_from_csv_lines(lines, orm_class):
    fields = orm_class.__table__.columns
    reader = csv.DictReader(lines)
    for row in reader:
        yield orm_class(
            **{k: read_value(v, fields[k]) for k, v in row.items() if k in fields}
        )


def read_value(value, field):
    # Treat the empty string as NULL
    if value == "":
        return None
    # The ORM will implicitly convert most types correctly from their string
    # representations, but not booleans
    if isinstance(field.type, sqlalchemy.Boolean):
        if value == "T":
            return True
        elif value == "F":
            return False
        else:
            # Let the ORM throw the error for us
            return value  # pragma: no cover
    return value
