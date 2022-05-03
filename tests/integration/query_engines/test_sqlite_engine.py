from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_model import (
    Function,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
)
from tests.lib.databases import InMemorySQLiteDatabase
from tests.lib.mock_backend import PatientLevelTable, backend_factory


def test_different_schema_for_same_table_doesnt_cause_a_problem():
    # This dataset definition has two references to the `patient_level_table` table which
    # have different schemas specified. This should not affect the operation of the engine
    # because schemas are only used for validation during construction of the query model,
    # not at query execution time.
    #
    # The query engine has to cache table instances internally to ensure that SQLAlchemy
    # correctly resolves table references. An earlier version of the query engine included
    # the schema in that caching which caused this test case to fail with an error like
    #
    #     sqlite3.OperationalError: ambiguous column name: patient_level_table.i1
    #
    # We don't expect this case to be encountered in production where the schema will
    # be consistently specified, but it's helpful to allow the schema to vary in some test
    # scenarios (specifically for the generative tests).
    variables = {
        "population": Function.Not(
            Function.IsNull(
                SelectColumn(
                    name="patient_id",
                    source=SelectPatientTable(
                        name="patient_level_table", schema=TableSchema(patient_id=int)
                    ),
                )
            )
        ),
        "v": SelectColumn(
            source=SelectPatientTable(
                name="patient_level_table", schema=TableSchema(i1=int)
            ),
            name="i1",
        ),
    }

    database = InMemorySQLiteDatabase()
    backend = backend_factory(SQLiteQueryEngine)
    engine = SQLiteQueryEngine(variables, backend(database.host_url()))
    database.setup(PatientLevelTable(PatientId=1))

    with engine.execute_query() as results:
        assert len(list(results)) == 1
