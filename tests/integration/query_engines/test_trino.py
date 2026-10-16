import contextlib
from unittest import mock

import pytest
import requests
import sqlalchemy
from sqlalchemy import Table
from sqlalchemy.engine import Connection
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import Select, visitors
from trino.exceptions import TrinoUserError

from ehrql.backends.base import DefaultSQLBackend
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
    # Define a simple query and load some test data
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
        # Raise some TABLE_NOT_FOUND errors to mimic the visibility lag on a
        # freshly created temporary table
        mock_execute.side_effect = [TABLE_NOT_FOUND_ERROR] * 3 + [None]
        results = trino_engine.extract(dataset)

    assert results == [
        {"patient_id": 1, "i": 10},
        {"patient_id": 2, "i": 20},
    ]
    assert mock_execute.call_count == 4
    assert sleep.call_count == 3


def test_backend_metadata_connection_args(trino_engine):
    backend = DefaultSQLBackend(
        trino_engine.query_engine_class,
        environ={"EHRQL_METADATA": '{"foo": "bar", "foo1": "bar1"}'},
    )
    query_engine = trino_engine.query_engine(backend=backend)
    with query_engine.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))
        query_id = result.cursor.query_id

    # Use the Trino REST API's /v1/query endpoint to confirm that the EHRQL_METADATA
    # from the backend were attached as clientTags to this query. This is an endpoint
    # used by the web UI (https://trino.io/docs/current/admin/web-interface.html) and
    # isn't officially documented, so it's possible this test could break in future, but
    # it's a nice simple way to check that the executed query included the client tags
    # we expected.
    # The official docs only document the v1/statement POST endpoint:
    # https://trino.io/docs/current/develop/client-protocol.html
    # The /v1/query endpoint is implemented here:
    # https://github.com/trinodb/trino/blob/0e59aa2b8bc5947e2357b268b56247045a9548b6/core/trino-main/src/main/java/io/trino/server/QueryResource.java#L59
    database = trino_engine.database
    session_info = requests.get(
        f"http://{database.host_from_host}:{database.port_from_host}/v1/query/{query_id}",
        headers={"X-Trino-User": database.username},
    ).json()
    assert session_info["session"]["clientTags"] == ["foo=bar", "foo1=bar1"]


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
        query, *_ = args
        if isinstance(query, query_type) and any(
            table_identifier in elem.name
            for elem in visitors.iterate(query.selectable)
            if isinstance(elem, Table)
        ):
            mocked(*args, **kwargs)
        return original(self, *args, **kwargs)

    with mock.patch.object(Connection, "execute", wrapper):
        yield mocked
