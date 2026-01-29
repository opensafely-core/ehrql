import datetime

import pytest
import sqlalchemy

from ehrql.backends.base import (
    DefaultSQLBackend,
    MappedTable,
    QueryTable,
    SQLBackend,
    ValidationError,
)
from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.query_model.nodes import Column, TableSchema
from ehrql.tables import PatientFrame, Series, table


class BackendFixture(SQLBackend):
    display_name = "Backend Fixture"
    query_engine_class = BaseSQLQueryEngine
    patient_join_column = "PatientId"

    practice_registrations = QueryTable(
        "SELECT patient_id, date_start, date_end FROM some_table"
    )

    @QueryTable.from_function
    def positive_tests(self):
        table_name = self.environ.get("table_name", "some_table")
        return f"SELECT patient_id, date FROM {table_name}"

    @QueryTable.from_function(materialize=True)
    def appointments(self):
        return "SELECT patient_id, date FROM some_table"


def test_backend_registers_tables():
    """Test that a backend registers its table names"""

    assert set(BackendFixture.tables) == {
        "practice_registrations",
        "positive_tests",
        "appointments",
    }


def test_query_table_sql():
    backend = BackendFixture()
    query_table = backend.tables["practice_registrations"]
    sql = query_table.get_query(backend)
    assert sql == "SELECT patient_id, date_start, date_end FROM some_table"


def test_query_table_from_function_sql():
    backend = BackendFixture(environ={"table_name": "other_table"})
    query_table = backend.tables["positive_tests"]
    sql = query_table.get_query(backend)
    assert sql == "SELECT patient_id, date FROM other_table"
    assert query_table.materialize is False


def test_query_table_from_function_sql_materialize():
    backend = BackendFixture()
    query_table = backend.tables["appointments"]
    sql = query_table.get_query(backend)
    assert sql == "SELECT patient_id, date FROM some_table"
    assert query_table.materialize is True


def test_default_backend_sql():
    backend = DefaultSQLBackend(query_engine_class=BaseSQLQueryEngine)
    table = backend.get_table_expression(
        "some_table", TableSchema(i=Column(int), b=Column(bool))
    )
    sql = str(sqlalchemy.select(table.c.patient_id, table.c.i, table.c.b))
    assert sql == (
        "SELECT some_table.patient_id, some_table.i, some_table.b \nFROM some_table"
    )


# Use a class as a convenient namespace (`types.SimpleNamespace` would also work)
class Schema:
    @table
    class patients(PatientFrame):
        date_of_birth = Series(datetime.date)


def test_backend_definition_is_allowed_extra_tables_and_columns():
    class BackendFixture(SQLBackend):
        display_name = "Backend Fixture"
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"
        implements = [Schema]

        patients = MappedTable(
            source="patient",
            columns=dict(date_of_birth="DoB", sex="sex"),
        )
        events = MappedTable(
            source="patient",
            columns=dict(date="date", code="code"),
        )

    assert BackendFixture


def test_backend_definition_accepts_query_table():
    class BackendFixture(SQLBackend):
        display_name = "Backend Fixture"
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"
        implements = [Schema]

        patients = QueryTable(
            "SELECT patient_id, CAST(DoB AS date) AS date_of_birth FROM patients",
        )

    assert BackendFixture


def test_backend_definition_fails_if_missing_tables():
    with pytest.raises(ValidationError, match="does not implement table"):

        class BackendFixture(SQLBackend):
            display_name = "Backend Fixture"
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"
            implements = [Schema]

            events = MappedTable(
                source="patient",
                columns=dict(date="date", code="code"),
            )


def test_backend_definition_fails_if_missing_column():
    with pytest.raises(ValidationError, match="missing columns"):

        class BackendFixture(SQLBackend):
            display_name = "Backend Fixture"
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"
            implements = [Schema]

            patients = MappedTable(
                source="patient",
                columns=dict(sex="sex"),
            )


def test_backend_definition_fails_if_query_table_missing_columns():
    with pytest.raises(ValidationError, match="SQL does not reference columns"):

        class BackendFixture(SQLBackend):
            display_name = "Backend Fixture"
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"
            implements = [Schema]

            patients = QueryTable(
                "SELECT patient_id, not_date_of_birth FROM patients",
            )
