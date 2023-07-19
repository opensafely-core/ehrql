import pytest


def test_driver_in_container(run_in_container, engine):
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

    run_in_container(
        [
            "test-connection",
            "--backend",
            backend,
            "--url",
            url,
        ]
    )
