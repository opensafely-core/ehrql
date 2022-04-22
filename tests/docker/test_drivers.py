import pytest


def test_driver_in_container(run_in_container, engine):
    if engine.name == "sqlite":
        pytest.xfail()

    backends = {
        "mssql": "tpp",
        "spark": "databricks",
    }

    if engine.name not in backends:
        assert False, f"no backend for database: {engine.name}"

    backend = backends[engine.name]
    url = engine.database.container_url()

    run_in_container(
        [
            "test_connection",
            "--backend",
            backend,
            "--url",
            url,
        ]
    )
