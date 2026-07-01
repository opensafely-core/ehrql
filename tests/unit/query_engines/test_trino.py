import logging
from unittest import mock

import pytest
from sqlalchemy.exc import OperationalError, ProgrammingError
from trino.exceptions import TrinoUserError


@pytest.fixture(autouse=True)
def set_log_level(caplog):
    caplog.set_level(logging.INFO)


TABLE_NOT_FOUND_ERROR = ProgrammingError(
    "",
    {},
    TrinoUserError(
        dict(errorName="TABLE_NOT_FOUND", message="Some table is not found")
    ),
)
OTHER_TRINO_USER_ERROR = ProgrammingError(
    "",
    {},
    TrinoUserError(
        dict(errorName="SOME_OTHER_ERROR", message="Some other sort of error")
    ),
)
OTHER_DBAPI_ERROR = OperationalError("", {}, Exception("Some other bad thing happened"))


def test_execute_query_no_results_with_retries(trino_engine, caplog):
    engine = trino_engine.query_engine()
    engine.max_retries = 3
    engine.retry_sleep = 1.0
    engine.backoff_factor = 2

    connection = mock.Mock(
        **{"execute.side_effect": [TABLE_NOT_FOUND_ERROR] * 3 + [None]}
    )

    with mock.patch("time.sleep") as sleep:
        engine.execute_query_no_results(connection, "")

    assert connection.execute.call_count == 4
    assert sleep.mock_calls == [mock.call(t) for t in [1.0, 2.0, 4.0]]
    assert "Retrying query (attempt 3 / 3)" in caplog.text


def test_execute_query_no_results_retries_exhausted(trino_engine):
    engine = trino_engine.query_engine()
    engine.max_retries = 3
    engine.retry_sleep = 1.0
    engine.backoff_factor = 2
    connection = mock.Mock(**{"execute.side_effect": [TABLE_NOT_FOUND_ERROR] * 4})

    with (
        mock.patch("time.sleep") as sleep,
        pytest.raises(ProgrammingError, match="Some table is not found"),
    ):
        engine.execute_query_no_results(connection, "")

    assert connection.execute.call_count == 4
    assert sleep.mock_calls == [mock.call(t) for t in [1.0, 2.0, 4.0]]


@pytest.mark.parametrize(
    "error", [OTHER_TRINO_USER_ERROR, OTHER_DBAPI_ERROR, Exception("An error")]
)
def test_execute_query_no_results_raises_other_errors(trino_engine, error):
    engine = trino_engine.query_engine()
    connection = mock.Mock(**{"execute.side_effect": [error]})

    with mock.patch("time.sleep") as sleep, pytest.raises(type(error)):
        engine.execute_query_no_results(connection, "")

    assert connection.execute.call_count == 1
    assert sleep.mock_calls == []


def test_execute_query_with_results_with_retries(trino_engine, caplog):
    engine = trino_engine.query_engine()
    engine.max_retries = 3
    engine.retry_sleep = 1.0
    engine.backoff_factor = 2
    connection = mock.Mock(
        **{"execute.side_effect": [TABLE_NOT_FOUND_ERROR] * 3 + [("it's", "OK", "now")]}
    )

    with mock.patch("time.sleep") as sleep:
        results = list(engine.execute_query_with_results(connection, ""))

    assert results == ["it's", "OK", "now"]
    assert connection.execute.call_count == 4
    assert sleep.mock_calls == [mock.call(t) for t in [1.0, 2.0, 4.0]]
    assert "Retrying query (attempt 3 / 3)" in caplog.text


def test_execute_query_with_results_retries_exhausted(trino_engine):
    engine = trino_engine.query_engine()
    engine.max_retries = 3
    engine.retry_sleep = 1.0
    engine.backoff_factor = 2
    connection = mock.Mock(**{"execute.side_effect": [TABLE_NOT_FOUND_ERROR] * 4})

    with (
        mock.patch("time.sleep") as sleep,
        pytest.raises(ProgrammingError, match="Some table is not found"),
    ):
        list(engine.execute_query_with_results(connection, ""))

    assert connection.execute.call_count == 4
    assert sleep.mock_calls == [mock.call(t) for t in [1.0, 2.0, 4.0]]


@pytest.mark.parametrize(
    "error", [OTHER_TRINO_USER_ERROR, OTHER_DBAPI_ERROR, Exception("An error")]
)
def test_execute_query_with_results_raises_other_errors(trino_engine, error):
    engine = trino_engine.query_engine()
    connection = mock.Mock(**{"execute.side_effect": [error]})

    with mock.patch("time.sleep") as sleep, pytest.raises(type(error)):
        list(engine.execute_query_with_results(connection, ""))

    assert connection.execute.call_count == 1
    assert sleep.mock_calls == []
