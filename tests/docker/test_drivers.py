import pytest

from tests.lib.docker import ContainerError


def test_driver_in_container(call_cli_docker, engine):
    # This test doesn't make sense for these in-memory databases
    if engine.name in {"in_memory", "sqlite"}:
        pytest.skip()

    backends = {
        "mssql": "ehrql.backends.tpp.TPPBackend",
        "trino": "ehrql.backends.emis.EMISBackend",
    }

    if engine.name not in backends:
        assert False, f"no backend for database: {engine.name}"

    backend = backends[engine.name]
    url = engine.database.container_url()

    call_cli_docker(
        "test-connection",
        "--backend",
        backend,
        "--url",
        url,
    )


def test_trino_certificates_from_environ_used_in_container(
    call_cli_docker, trino_engine
):
    # The SSLError shows that the values from the environ reached the container, and
    # that the files were written and then read. Trino requires https for certificate
    # auth, so a real connection isn't possible with the test Trino that only supports
    # http.
    with pytest.raises(ContainerError, match="SSLError.+PEM"):
        call_cli_docker(
            "test-connection",
            "--backend",
            "ehrql.backends.emisv2.EMISV2Backend",
            "--url",
            trino_engine.database.container_url(),
            environ={
                "TRINO_TLS_CERT": (
                    "-----BEGIN CERTIFICATE-----\nfake\n-----END CERTIFICATE-----\n"
                ),
                "TRINO_TLS_KEY": (
                    "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n"
                ),
            },
        )
