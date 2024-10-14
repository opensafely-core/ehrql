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

    patients = MappedTable(
        source="Patient",
        columns=dict(
            patient_id="PatID",
            date_of_birth="DateOfBirth",
        ),
    )

    events = MappedTable(
        source="events",
        columns=dict(
            date="date",
        ),
    )

    practice_registrations = QueryTable(
        "SELECT patient_id, date_start, date_end FROM some_table"
    )

    @QueryTable.from_function
    def positive_tests(self):
        table_name = self.config.get("table_name", "some_table")
        return f"SELECT patient_id, date FROM {table_name}"


def test_backend_registers_tables():
    """Test that a backend registers its table names"""

    assert set(BackendFixture.tables) == {
        "patients",
        "events",
        "practice_registrations",
        "positive_tests",
    }


def test_mapped_table_sql_with_modified_names():
    table = BackendFixture().get_table_expression(
        "patients",
        TableSchema(
            date_of_birth=Column(datetime.date),
        ),
    )
    sql = str(sqlalchemy.select(table.c.patient_id, table.c.date_of_birth))
    assert sql == 'SELECT "Patient"."PatID", "Patient"."DateOfBirth" \nFROM "Patient"'


def test_mapped_table_sql_with_matching_names():
    table = BackendFixture().get_table_expression(
        "events",
        TableSchema(
            date=Column(datetime.date),
        ),
    )
    sql = str(sqlalchemy.select(table.c.patient_id, table.c.date))
    assert sql == 'SELECT events."PatientId", events.date \nFROM events'


def test_query_table_sql():
    table = BackendFixture().get_table_expression(
        "practice_registrations",
        TableSchema(
            date_start=Column(datetime.date),
            date_end=Column(datetime.date),
        ),
    )
    sql = str(sqlalchemy.select(table.c.patient_id, table.c.date_start))
    assert sql == (
        "SELECT practice_registrations.patient_id, practice_registrations.date_start \n"
        "FROM (SELECT patient_id, date_start, date_end FROM some_table) AS "
        "practice_registrations"
    )


def test_query_table_from_function_sql():
    backend = BackendFixture(config={"table_name": "other_table"})
    table = backend.get_table_expression(
        "positive_tests",
        TableSchema(date=Column(datetime.date)),
    )
    assert str(table) == "SELECT patient_id, date FROM other_table"


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
