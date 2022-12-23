import contextlib
from unittest import mock

import pytest
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.future.engine import Connection
from sqlalchemy.sql import Select

from databuilder.query_engines.mssql import MSSQLQueryEngine
from databuilder.query_model.nodes import (
    AggregateByPatient,
    Column,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
)
from databuilder.utils.orm_utils import orm_classes_from_tables


def test_get_results_using_temporary_database(mssql_database):
    temp_database_name = "temp_tables"

    # Define a simple query and load some test data
    patient_table = SelectPatientTable("patients", TableSchema(i=Column(int)))
    variable_definitions = dict(
        population=AggregateByPatient.Exists(patient_table),
        i=SelectColumn(patient_table, "i"),
    )
    patients = orm_classes_from_tables([patient_table])["patients"]
    mssql_database.setup(
        patients(patient_id=1, i=10),
        patients(patient_id=2, i=20),
    )
    query_engine = MSSQLQueryEngine(
        mssql_database.host_url(),
        config=dict(TEMP_DATABASE_NAME=temp_database_name),
    )

    with wrap_select_queries() as select, mock.patch("time.sleep") as sleep:
        # We want the first two SELECT queries to fail but the third to succeed
        select.side_effect = [
            OperationalError("fail", None, None),
            OperationalError("fail again", None, None),
            None,
        ]

        results = query_engine.get_results(variable_definitions)

        assert list(results) == [(1, 10), (2, 20)]
        assert select.call_count == 3
        # We expect to sleep after each failure
        assert sleep.call_count == 2
        # Grab a reference to the SELECT query so we can use it later
        query = select.call_args[0][0]

    # Check that we were actually using the temporary database
    assert temp_database_name in str(query)
    # Check that the table we were querying has now been cleaned up
    with mssql_database.engine().connect() as conn:
        with pytest.raises(ProgrammingError, match="Invalid object name"):
            conn.execute(query)


@contextlib.contextmanager
def wrap_select_queries():
    """
    Intercept SELECT queries so we can track them, and optionally raise exceptions,
    while still calling the original database methods and passing the result through
    """
    original = Connection.execute
    mocked = mock.Mock()

    def wrapper(self, *args, **kwargs):
        if args and isinstance(args[0], Select):
            mocked(*args, **kwargs)
        return original(self, *args, **kwargs)

    with mock.patch.object(Connection, "execute", wrapper):
        yield mocked
