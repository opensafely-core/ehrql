import sqlalchemy
import sqlalchemy.orm

import databuilder.backends.base as backends
from databuilder.query_model import (
    AggregateByPatient,
    Function,
    SelectPatientTable,
    SelectTable,
)


def setup(schema, num_patient_tables, num_event_tables):
    registry = sqlalchemy.orm.registry()
    ids = iter(range(1, 2**63)).__next__
    patient_id_column = "PatientId"

    patient_table_names, patient_classes = _build_orm_classes(
        "p", num_patient_tables, schema, patient_id_column, ids, registry
    )
    event_table_names, event_classes = _build_orm_classes(
        "e", num_event_tables, schema, patient_id_column, ids, registry
    )

    table_names = patient_table_names + event_table_names
    backend = _make_backend(table_names, schema, patient_id_column)

    all_patients_query = _build_query(patient_table_names, event_table_names)

    return (
        patient_id_column,
        patient_classes,
        event_classes,
        backend,
        all_patients_query,
    )


def _build_orm_classes(prefix, count, schema, patient_id_column, ids, registry):
    names = [f"{prefix}{i}" for i in range(count)]
    classes = [
        _build_orm_class(name, schema, patient_id_column, ids, registry)
        for name in names
    ]
    return names, classes


def _build_orm_class(name, schema, patient_id_column, ids, registry):
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

    # It's helpful to have the classes available as module properties so that we can copy-paste failing test cases
    # from Hypothesis.
    globals()[name] = class_

    return class_


def _make_backend(table_names, schema, patient_id_column):
    tables = _backend_tables(schema, table_names)
    class_vars = {
        "backend_id": "gen-test-backend",
        "query_engine_class": "not-needed",
        "patient_join_column": patient_id_column,
    } | tables
    return type("Backend", (backends.BaseBackend,), class_vars)


def _backend_tables(schema, table_names):
    table_columns = _backend_columns(schema)

    tables = {}
    for name in table_names:
        tables[name] = _backend_table(name, table_columns)
    return tables


def _backend_columns(schema):
    return {name: _backend_column(name, type_) for name, type_ in schema.items()}


def _backend_column(name, type_):
    type_map = {int: "integer", bool: "boolean"}
    return backends.Column(type_map[type_], source=name)


def _backend_table(name, columns):
    return backends.MappedTable(implements=None, source=name, columns=columns)


def _build_query(patient_tables, event_tables):
    # Note that we do not include a schema for the tables here. This is because we are accessing the patient_id
    # which isn't included in the schema for simplicity elsewhere. There is no downside to not having the schema
    # because these queries don't mention any other columns, so we don't miss out on possible type-checking.
    clauses = []

    for table in patient_tables:
        clauses.append(AggregateByPatient.Exists(source=SelectPatientTable(name=table)))

    for table in event_tables:
        clauses.append(AggregateByPatient.Exists(source=SelectTable(name=table)))

    return _join_with_or(clauses)


def _join_with_or(clauses):
    query = clauses[0]
    for clause in clauses[1:]:
        query = Function.Or(query, clause)
    return query
