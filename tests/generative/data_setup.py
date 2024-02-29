from ehrql.query_model.nodes import (
    AggregateByPatient,
    Function,
    SelectPatientTable,
    SelectTable,
)
from tests.lib.orm_utils import orm_classes_from_tables


def setup(schema, num_patient_tables, num_event_tables):
    patient_tables = [
        SelectPatientTable(f"p{i}", schema=schema) for i in range(num_patient_tables)
    ]
    event_tables = [
        SelectTable(f"e{i}", schema=schema) for i in range(num_event_tables)
    ]
    all_tables = patient_tables + event_tables

    orm_classes = orm_classes_from_tables(all_tables)
    _add_classes_to_module_namespace(orm_classes)

    patient_classes = [orm_classes[table.name] for table in patient_tables]
    event_classes = [orm_classes[table.name] for table in event_tables]

    all_patients_query = _build_query(all_tables)

    # We arbitrarily choose the first patient class, but all the ORM classes share the
    # same MetaData
    metadata = patient_classes[0].metadata

    return (
        patient_classes,
        event_classes,
        all_patients_query,
        metadata,
    )


def _add_classes_to_module_namespace(orm_classes):
    # It's helpful to have the classes available as module properties so that we can
    # copy-paste failing test cases from Hypothesis. These classes naturally believe
    # that they belong to the `orm_utils` module which created them, so we have to
    # re-parent them here. We use only the final component of the module name as that's
    # how we import it in `test_query_model`.
    for class_ in orm_classes.values():
        class_.__module__ = __name__.rpartition(".")[2]
        globals()[class_.__name__] = class_


def _build_query(tables):
    clauses = [AggregateByPatient.Exists(source=table) for table in tables]
    return _join_with_or(clauses)


def _join_with_or(clauses):
    query = clauses[0]
    for clause in clauses[1:]:
        query = Function.Or(query, clause)
    return query
