import contextlib
from unittest import mock

import pytest
from sqlalchemy import Table
from sqlalchemy.engine import Connection
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import Select, visitors
from trino.exceptions import TrinoUserError

from ehrql.query_model.nodes import (
    AggregateByPatient,
    Column,
    Dataset,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
)
from ehrql.utils.sqlalchemy_query_utils import CreateTableAs


TABLE_NOT_FOUND_ERROR = ProgrammingError(
    "",
    {},
    TrinoUserError(
        dict(errorName="TABLE_NOT_FOUND", message="Some table is not found")
    ),
)


@pytest.mark.parametrize(
    "query_type,table_identifier",
    [
        # Only raise the TABLE_NOT_FOUND error on the CREATE TABLE query
        # that uses a temp table
        pytest.param(CreateTableAs, "tmp_1", id="retry-on-create-table"),
        pytest.param(Select, "tmp_2", id="retry-on-select"),
    ],
)
def test_execute_query_with_retries_on_table_not_found_errors(
    trino_engine, query_type, table_identifier
):
    patient_table = SelectPatientTable("patients", TableSchema(i=Column(int)))
    dataset = Dataset(
        population=AggregateByPatient.Exists(patient_table),
        variables={"i": SelectColumn(patient_table, "i")},
        events={},
        measures=None,
    )
    trino_engine.populate(
        {
            patient_table: [
                dict(patient_id=1, i=10),
                dict(patient_id=2, i=20),
            ]
        }
    )
    with (
        wrap_query(query_type, table_identifier) as mock_execute,
        mock.patch("time.sleep") as sleep,
    ):
        mock_execute.side_effect = [TABLE_NOT_FOUND_ERROR] * 3 + [None]
        results = trino_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "i": 10},
        {"patient_id": 2, "i": 20},
    ]
    assert mock_execute.call_count == 4
    assert sleep.call_count == 3


@contextlib.contextmanager
def wrap_query(query_type, table_identifier):
    """
    Intercept queries of a given type if it selects from a table
    whose name contains table_identifier.
    Optionally raise exceptions while still calling the original
    database methods and passing results through if applicable.
    """
    original = Connection.execute
    mocked = mock.Mock()

    def wrapper(self, *args, **kwargs):
        if args:
            query = args[0]
            if isinstance(query, query_type) and any(
                table_identifier in elem.name
                for elem in visitors.iterate(query.selectable)
                if isinstance(elem, Table)
            ):
                mocked(*args, **kwargs)
        return original(self, *args, **kwargs)

    with mock.patch.object(Connection, "execute", wrapper):
        yield mocked
