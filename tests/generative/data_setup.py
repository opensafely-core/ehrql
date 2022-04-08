import sqlalchemy
import sqlalchemy.orm

from databuilder.backends.base import BaseBackend


def setup(schema, num_patient_tables, num_event_tables):
    registry = sqlalchemy.orm.registry()
    ids = iter(range(1, 2**63)).__next__
    patient_id_column = "PatientId"

    patient_tables = build_tables(
        "p", num_patient_tables, schema, patient_id_column, ids, registry
    )
    event_tables = build_tables(
        "e", num_event_tables, schema, patient_id_column, ids, registry
    )

    return (
        patient_id_column,
        patient_tables,
        event_tables,
        make_backend(patient_id_column),
    )


def build_tables(prefix, count, schema, patient_id_column, ids, registry):
    patient_tables = [
        build_table(f"{prefix}{i}", schema, patient_id_column, ids, registry)
        for i in range(count)
    ]
    return patient_tables


def build_table(name, schema, patient_id_column, ids, registry):
    columns = [
        sqlalchemy.Column("Id", sqlalchemy.Integer, primary_key=True, default=ids),
        sqlalchemy.Column(patient_id_column, sqlalchemy.Integer),
    ]
    for col_name, type_ in schema.items():
        sqla_type = {int: sqlalchemy.Integer, bool: sqlalchemy.Boolean}[type_]
        columns.append(sqlalchemy.Column(col_name, sqla_type))

    table = sqlalchemy.Table(name, registry.metadata, *columns)
    class_ = type(name, (object,), dict(__tablename__=name, metadata=registry.metadata))
    registry.map_imperatively(class_, table)

    return class_


def make_backend(patient_id_column_):
    class Backend(BaseBackend):
        backend_id = "gen-test-backend"
        query_engine_class = "not-needed"
        patient_join_column = patient_id_column_

    return Backend
