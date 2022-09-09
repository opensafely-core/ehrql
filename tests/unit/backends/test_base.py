import datetime

import pytest
import sqlalchemy

from databuilder.backends.base import (
    BaseBackend,
    DefaultBackend,
    MappedTable,
    QueryTable,
    ValidationError,
)
from databuilder.query_engines.base_sql import BaseSQLQueryEngine
from databuilder.tables import PatientFrame, Series, table


class TestBackend(BaseBackend):
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


def test_backend_registers_tables():
    """Test that a backend registers its table names"""

    assert set(TestBackend.tables) == {
        "patients",
        "events",
        "practice_registrations",
    }


def test_mapped_table_sql_with_modified_names():
    table = TestBackend().get_table_expression(
        "patients",
        {
            "date_of_birth": datetime.date,
        },
    )
    sql = str(sqlalchemy.select(table.c.patient_id, table.c.date_of_birth))
    assert sql == 'SELECT "Patient"."PatID", "Patient"."DateOfBirth" \nFROM "Patient"'


def test_mapped_table_sql_with_matching_names():
    table = TestBackend().get_table_expression(
        "events",
        {
            "date": datetime.date,
        },
    )
    sql = str(sqlalchemy.select(table.c.patient_id, table.c.date))
    assert sql == 'SELECT events."PatientId", events.date \nFROM events'


def test_query_table_sql():
    table = TestBackend().get_table_expression(
        "practice_registrations",
        {
            "date_start": datetime.date,
            "date_end": datetime.date,
        },
    )
    sql = str(sqlalchemy.select(table.c.patient_id, table.c.date_start))
    assert sql == (
        "SELECT practice_registrations.patient_id, practice_registrations.date_start \n"
        "FROM (SELECT patient_id, date_start, date_end FROM some_table) AS "
        "practice_registrations"
    )


def test_default_backend_sql():
    table = DefaultBackend().get_table_expression("some_table", {"i": int, "b": bool})
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
    class TestBackend(BaseBackend):
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"
        implements = [Schema]

        patients = MappedTable(
            source="patient",
            columns=dict(date_of_birth="date_of_birth", sex="sex"),
        )
        events = MappedTable(
            source="patient",
            columns=dict(date="date", code="code"),
        )

    assert TestBackend


def test_backend_definition_accepts_query_table():
    class TestBackend(BaseBackend):
        query_engine_class = BaseSQLQueryEngine
        patient_join_column = "patient_id"
        implements = [Schema]

        patients = QueryTable(
            "SELECT patient_id, CAST(DoB AS date) AS date_of_birth FROM patients",
        )

    assert TestBackend


def test_backend_definition_fails_if_missing_tables():
    with pytest.raises(ValidationError, match="does not implement table"):

        class TestBackend(BaseBackend):
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"
            implements = [Schema]

            events = MappedTable(
                source="patient",
                columns=dict(date="date", code="code"),
            )


def test_backend_definition_fails_if_missing_column():
    with pytest.raises(ValidationError, match="missing columns"):

        class TestBackend(BaseBackend):
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"
            implements = [Schema]

            patients = MappedTable(
                source="patient",
                columns=dict(sex="sex"),
            )


def test_backend_definition_fails_if_query_table_missing_columns():
    with pytest.raises(ValidationError, match="SQL does not reference columns"):

        class TestBackend(BaseBackend):
            query_engine_class = BaseSQLQueryEngine
            patient_join_column = "patient_id"
            implements = [Schema]

            patients = QueryTable(
                "SELECT patient_id, not_date_of_birth FROM patients",
            )
