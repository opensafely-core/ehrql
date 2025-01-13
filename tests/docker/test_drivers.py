import pytest


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
