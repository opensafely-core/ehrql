import logging
from pathlib import Path
from unittest import mock

import pytest
from sqlalchemy import event
from sqlalchemy.exc import OperationalError, ProgrammingError
from trino.auth import CertificateAuthentication
from trino.exceptions import TrinoUserError

from ehrql.query_engines.trino import TrinoQueryEngine


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


def test_execute_query_with_retries(trino_engine, caplog):
    engine = trino_engine.query_engine()
    engine.max_retries = 3
    engine.retry_sleep = 1.0
    engine.backoff_factor = 2

    connection = mock.Mock(
        **{"execute.side_effect": [TABLE_NOT_FOUND_ERROR] * 3 + [None]}
    )

    with mock.patch("time.sleep") as sleep:
        engine.execute_query(connection, "")

    assert connection.execute.call_count == 4
    assert sleep.mock_calls == [mock.call(t) for t in [1.0, 2.0, 4.0]]
    assert "Retrying query (attempt 3 / 3)" in caplog.text


def test_execute_query_retries_exhausted(trino_engine):
    engine = trino_engine.query_engine()
    engine.max_retries = 3
    engine.retry_sleep = 1.0
    engine.backoff_factor = 2
    connection = mock.Mock(**{"execute.side_effect": [TABLE_NOT_FOUND_ERROR] * 4})

    with (
        mock.patch("time.sleep") as sleep,
        pytest.raises(ProgrammingError, match="Some table is not found"),
    ):
        engine.execute_query(connection, "")

    assert connection.execute.call_count == 4
    assert sleep.mock_calls == [mock.call(t) for t in [1.0, 2.0, 4.0]]


@pytest.mark.parametrize(
    "error", [OTHER_TRINO_USER_ERROR, OTHER_DBAPI_ERROR, Exception("An error")]
)
def test_execute_query_raises_other_errors(trino_engine, error):
    engine = trino_engine.query_engine()
    connection = mock.Mock(**{"execute.side_effect": [error]})

    with mock.patch("time.sleep") as sleep, pytest.raises(type(error)):
        engine.execute_query(connection, "")

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


def capture_connect_params(query_engine):
    captured = {}

    @event.listens_for(query_engine.engine, "do_connect")
    def _capture(dialect, conn_rec, cargs, cparams):
        captured.update(cparams)

    query_engine.engine.connect()

    return captured


def test_client_tags_passed_to_driver(trino_engine):
    query_engine = trino_engine.query_engine(dsn=trino_engine.database.host_url())
    query_engine.backend = mock.Mock(metadata={"foo": "bar"})
    params = capture_connect_params(query_engine)
    assert params["client_tags"] == ["foo=bar"]


def test_client_tags_no_metadata(trino_engine):
    query_engine = trino_engine.query_engine(dsn=trino_engine.database.host_url())
    query_engine.backend = mock.Mock(metadata={})
    params = capture_connect_params(query_engine)
    assert "client_tags" not in params


@pytest.fixture
def tls_query_engine(request):
    """
    Fixture that creates a TrinoQueryEngine with TLS cert env variables and
    explicitly cleans up its TemporaryDirectory afterwards. The temp directory
    would be removed anyway on garbage collection, but implicitly, which makes
    it emit a ResourceWarning.
    """
    # Tests can add additional environ by parametrizing this fixture indirectly
    extra_environ = getattr(request, "param", {})
    environ = {
        "TRINO_TLS_CERT": "cert-content",
        "TRINO_TLS_KEY": "key-content",
        **extra_environ,
    }
    query_engine = TrinoQueryEngine(None, environ=environ)
    yield query_engine
    query_engine._tls_dir.cleanup()


def test_certificate_auth_configured_from_environ(tls_query_engine):
    connect_args = tls_query_engine.get_sqlalchemy_execution_options()["connect_args"]
    tls_dir = Path(tls_query_engine._tls_dir.name)

    assert connect_args == {
        "auth": CertificateAuthentication(
            str(tls_dir / "cert.pem"), str(tls_dir / "key.pem")
        ),
        "http_scheme": "https",
    }
    assert (tls_dir / "cert.pem").read_text() == "cert-content"
    assert (tls_dir / "key.pem").read_text() == "key-content"


@pytest.mark.parametrize(
    "tls_query_engine",
    [{"EHRQL_METADATA": '{"foo": "bar"}'}],
    indirect=True,
)
def test_certificate_auth_with_client_tags(tls_query_engine):
    connect_args = tls_query_engine.get_sqlalchemy_execution_options()["connect_args"]

    assert connect_args["client_tags"] == ["foo=bar"]
    assert isinstance(connect_args["auth"], CertificateAuthentication)


@pytest.mark.parametrize(
    "environ",
    [
        {},
        {"TRINO_TLS_CERT": "cert-content"},
        {"TRINO_TLS_KEY": "key-content"},
    ],
)
def test_no_certificate_auth_without_both_cert_and_key(environ):
    query_engine = TrinoQueryEngine(None, environ=environ)
    assert query_engine.get_sqlalchemy_execution_options() == {}
    assert not hasattr(query_engine, "_tls_dir")
