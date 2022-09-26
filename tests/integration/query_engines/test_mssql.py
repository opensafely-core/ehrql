from sqlalchemy.orm import declarative_base

from databuilder.orm_factory import orm_class_from_qm_table
from databuilder.query_engines.mssql import MSSQLQueryEngine
from databuilder.query_model import (
    AggregateByPatient,
    Column,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
)


def test_get_results_using_temporary_database(mssql_database):
    temp_database_name = "temp_tables"

    # Define a simple query and load some test data
    patient_table = SelectPatientTable("patients", TableSchema(i=Column(int)))
    variable_definitions = dict(
        population=AggregateByPatient.Exists(patient_table),
        i=SelectColumn(patient_table, "i"),
    )
    patients = orm_class_from_qm_table(declarative_base(), patient_table)
    mssql_database.setup(
        patients(patient_id=1, i=10),
        patients(patient_id=2, i=20),
    )
    query_engine = MSSQLQueryEngine(
        mssql_database.host_url(),
        config=dict(TEMP_DATABASE_NAME=temp_database_name),
    )

    results = query_engine.get_results(variable_definitions)

    assert list(results) == [(1, 10), (2, 20)]
