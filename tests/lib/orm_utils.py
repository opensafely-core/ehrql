import functools

import sqlalchemy
from sqlalchemy.orm import declarative_base

from ehrql.query_model.nodes import has_one_row_per_patient
from ehrql.sqlalchemy_types import type_from_python_type


SYNTHETIC_PRIMARY_KEY = "row_id"


def orm_class_from_schema(base_class, table_name, schema, has_one_row_per_patient):
    """
    Given a SQLAlchemy ORM "declarative base" class, a table name and a TableSchema,
    return a ORM class with the appropriate columns
    """
    attributes = {"__tablename__": table_name}

    if has_one_row_per_patient:
        attributes["patient_id"] = make_primary_key_column()
    else:
        attributes["patient_id"] = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
        attributes[SYNTHETIC_PRIMARY_KEY] = make_primary_key_column()

    for col_name, type_ in schema.column_types:
        attributes[col_name] = sqlalchemy.Column(type_from_python_type(type_))

    class_name = table_name.title().replace("_", "")

    return type(class_name, (base_class,), attributes)


def make_primary_key_column():
    return sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        # We deliberately avoid using database-level autoincrement and instead implement
        # our own sequence generation. In MSSQL using autoincrement creates "identity
        # columns" which [cause us problems][1400]. And not all DBMSs we plan to support
        # have autoincrement features in any case. Given that these are the tables in
        # question are test fixtures which we control the usual concurrency and
        # integrity concerns don't apply.
        #
        # 1400: https://github.com/opensafely-core/ehrql/pull/1400
        autoincrement=False,
        default=iter(range(1, 2**63)).__next__,
    )


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
        table_name = table._qm_node.name if hasattr(table, "_qm_node") else table.name
        orm_class = orm_classes[table_name]
        yield from (orm_class(**row) for row in rows)


def orm_classes_from_tables(tables):
    """
    Takes an iterable of tables (either ehrQL tables or query model tables) and returns
    a dict mapping table names to ORM classes
    """
    qm_tables = frozenset(
        table._qm_node if hasattr(table, "_qm_node") else table for table in tables
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
