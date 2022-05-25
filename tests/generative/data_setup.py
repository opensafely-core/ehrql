import sqlalchemy
import sqlalchemy.orm

from databuilder.query_model import (
    AggregateByPatient,
    Function,
    SelectPatientTable,
    SelectTable,
)
from databuilder.sqlalchemy_types import Integer, type_from_python_type

from ..lib.util import next_id, null


def setup(schema, num_patient_tables, num_event_tables):
    registry = sqlalchemy.orm.registry()
    patient_id_column = "patient_id"

    patient_table_names, patient_classes = _build_orm_classes(
        "p", num_patient_tables, schema, patient_id_column, registry
    )
    event_table_names, event_classes = _build_orm_classes(
        "e", num_event_tables, schema, patient_id_column, registry
    )

    all_patients_query = _build_query(patient_table_names, event_table_names, schema)

    return (
        patient_id_column,
        patient_classes,
        event_classes,
        all_patients_query,
        registry.metadata,
    )


def _build_orm_classes(prefix, count, schema, patient_id_column, registry):
    names = [f"{prefix}{i}" for i in range(count)]
    classes = [
        _build_orm_class(name, schema, patient_id_column, registry) for name in names
    ]
    return names, classes


def _build_orm_class(name, schema, patient_id_column, registry):
    columns = [
        sqlalchemy.Column("Id", Integer, primary_key=True, default=next_id),
        sqlalchemy.Column(patient_id_column, Integer, nullable=False),
    ]
    for col_name, type_ in schema.items():
        columns.append(
            sqlalchemy.Column(col_name, type_from_python_type(type_), default=null)
        )

    table = sqlalchemy.Table(name, registry.metadata, *columns)
    class_ = type(name, (object,), dict(__tablename__=name, metadata=registry.metadata))
    registry.map_imperatively(class_, table)

    # It's helpful to have the classes available as module properties so that we can copy-paste failing test cases
    # from Hypothesis.
    globals()[name] = class_

    return class_


def _build_query(patient_tables, event_tables, schema):
    clauses = []

    for table in patient_tables:
        clauses.append(
            AggregateByPatient.Exists(
                source=SelectPatientTable(name=table, schema=schema)
            )
        )

    for table in event_tables:
        clauses.append(
            AggregateByPatient.Exists(source=SelectTable(name=table, schema=schema))
        )

    return _join_with_or(clauses)


def _join_with_or(clauses):
    query = clauses[0]
    for clause in clauses[1:]:
        query = Function.Or(query, clause)
    return query
