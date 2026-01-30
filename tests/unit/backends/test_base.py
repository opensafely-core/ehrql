import datetime

import pytest

from ehrql.backends.base import (
    MappedTable,
    QueryTable,
    SQLBackend,
    ValidationError,
)
from ehrql.query_engines.base_sql import BaseSQLQueryEngine
from ehrql.tables import PatientFrame, Series, table


class BackendFixture(SQLBackend):
    display_name = "Backend Fixture"
    query_engine_class = BaseSQLQueryEngine
    patient_join_column = "patient_id"

    query_table_1 = QueryTable("SELECT * FROM query_table")

    query_table_2 = QueryTable("SELECT * FROM query_table", materialize=True)

    @QueryTable.from_function
    def query_table_3(self):
        return f"SELECT * FROM {self.environ['table_name']}"

    @QueryTable.from_function(materialize=True)
    def query_table_4(self):
        return f"SELECT * FROM {self.environ['table_name']}"


def test_backend_registers_tables():
    """Test that a backend registers its table names"""

    assert set(BackendFixture.tables) == {
        "query_table_1",
        "query_table_2",
        "query_table_3",
        "query_table_4",
    }


@pytest.mark.parametrize(
    "table,expect_sql,expect_materialize",
    [
        ("query_table_1", "SELECT * FROM query_table", False),
        ("query_table_2", "SELECT * FROM query_table", True),
        ("query_table_3", "SELECT * FROM some_table", False),
        ("query_table_4", "SELECT * FROM some_table", True),
    ],
)
def test_query_table(table, expect_sql, expect_materialize):
    backend = BackendFixture(environ={"table_name": "some_table"})
    query_table = backend.tables[table]
    sql = query_table.get_query(backend)
    assert sql == expect_sql
    assert query_table.materialize == expect_materialize


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
