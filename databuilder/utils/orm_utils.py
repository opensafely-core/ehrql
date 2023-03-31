import csv
import datetime
import functools
from contextlib import ExitStack

import sqlalchemy
from sqlalchemy.orm import declarative_base

from databuilder.query_model.nodes import has_one_row_per_patient
from databuilder.sqlalchemy_types import type_from_python_type


SYNTHETIC_PRIMARY_KEY = "row_id"


def orm_class_from_schema(base_class, table_name, schema, has_one_row_per_patient):
    """
    Given a SQLAlchemy ORM "declarative base" class, a table name and a TableSchema,
    return a ORM class with the appropriate columns
    """
    attributes = {"__tablename__": table_name}

    if has_one_row_per_patient:
        attributes["patient_id"] = sqlalchemy.Column(
            sqlalchemy.Integer, primary_key=True
        )
    else:
        attributes["patient_id"] = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
        attributes[SYNTHETIC_PRIMARY_KEY] = sqlalchemy.Column(
            sqlalchemy.Integer, primary_key=True
        )

    for col_name, type_ in schema.column_types:
        attributes[col_name] = sqlalchemy.Column(type_from_python_type(type_))

    class_name = table_name.title().replace("_", "")

    return type(class_name, (base_class,), attributes)


def make_orm_models(*args):
    """
    Takes one or many dicts like:
        {
            patients: [dict(patient_id=1, sex="male")],
            events: [
                dict(patient_id=1, code="abc"),
                dict(patient_id=1, code="xyz"),
            ]
        }

    Where the keys are tables (either ehrQL tables or query model tables) and the values
    are lists of rows. Yields a sequence of ORM model instances.
    """
    # Merge the supplied dicts so we can get the full set of tables used upfront
    combined = {}
    for table_data in args:
        for table, rows in table_data.items():
            combined.setdefault(table, []).extend(rows)
    orm_classes = orm_classes_from_tables(combined.keys())
    for table, rows in combined.items():
        table_name = table.qm_node.name if hasattr(table, "qm_node") else table.name
        orm_class = orm_classes[table_name]
        yield from (orm_class(**row) for row in rows)


def orm_classes_from_tables(tables):
    """
    Takes an iterable of tables (either ehrQL tables or query model tables) and returns
    a dict mapping table names to ORM classes
    """
    qm_tables = frozenset(
        table.qm_node if hasattr(table, "qm_node") else table for table in tables
    )
    return _orm_classes_from_qm_tables(qm_tables)


# Apply caching so that when large numbers of tests use the same tables we aren't
# constantly recreating ORM classes
@functools.cache
def _orm_classes_from_qm_tables(qm_tables: frozenset):
    Base = declarative_base()
    return {
        table.name: orm_class_from_schema(
            Base, table.name, table.schema, has_one_row_per_patient(table)
        )
        for table in qm_tables
    }


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
    if isinstance(field.type, sqlalchemy.Boolean):
        if value == "T":
            return True
        elif value == "F":
            return False
        else:
            raise ValueError(f"invalid boolean '{value}', must be 'T' or 'F'")
    elif isinstance(field.type, sqlalchemy.Date):
        return datetime.date.fromisoformat(value)
    elif isinstance(field.type, sqlalchemy.Float):
        return float(value)
    elif isinstance(field.type, sqlalchemy.Integer):
        return int(value)
    elif isinstance(field.type, sqlalchemy.String):
        return value
    else:
        assert False


def write_orm_models_to_csv_directory(directory, models):
    directory.mkdir(exist_ok=True)
    writers = {}
    with ExitStack() as stack:
        for model in models:
            orm_class = model.__class__

            write_row = writers.get(orm_class)
            if write_row is None:
                fileobj = stack.enter_context(
                    open(directory / f"{orm_class.__tablename__}.csv", "w", newline="")
                )
                write_row = orm_csv_writer(fileobj, orm_class)
                writers[orm_class] = write_row

            write_row(model)


def orm_csv_writer(fileobj, orm_class):
    fields = {
        name: field
        for (name, field) in orm_class.__table__.columns.items()
        if name != SYNTHETIC_PRIMARY_KEY
    }
    writer = csv.DictWriter(fileobj, fields.keys())
    writer.writeheader()

    def write_model(model):
        row = {
            name: format_value(getattr(model, name), field)
            for name, field in fields.items()
        }
        writer.writerow(row)

    return write_model


def format_value(value, field):
    # The CSV library will implicitly format most types correctly as strings, but
    # doesn't handle booleans as we'd like
    if isinstance(field.type, sqlalchemy.Boolean):
        if value is True:
            return "T"
        elif value is False:
            return "F"
        elif value is None:
            return ""
        else:
            assert False
    return value
