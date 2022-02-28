from unittest import mock

import pytest
import sqlalchemy

from databuilder.query_engines.mssql_lib import (
    ReconnectableConnection,
    assert_temporary_tables_writable,
)


def test_reconnectableconnection_exit_with_no_connection():
    conn = ReconnectableConnection(None)
    conn._conn = None
    assert conn.__exit__() is None


def test_reconnectableconnection_reconnect_with_no_connection():
    with ReconnectableConnection(None) as conn:
        conn.reconnect()
        conn.reconnect()


def test_assert_temporary_tables_writable_exception_wrapper():
    conn = mock.MagicMock()
    conn.execute.side_effect = sqlalchemy.exc.DBAPIError(None, None, None)

    match = "^Unable to write temporary table with prefix 'unknown_table'$"
    with pytest.raises(RuntimeError, match=match):
        assert_temporary_tables_writable(conn, "unknown_table")
