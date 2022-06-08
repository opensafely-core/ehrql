from types import SimpleNamespace

import pytest


# TODO: Until we move the mssql and spark engines back from "legacy" status the default
# engine fixture doesn't give us the coverage we need so we replace it here. Once these
# are included in the default engine fixture we can delete this one. But we'll also need
# to add a check the test to skip on the in-memory and SQLite engines because the test
# won't apply to them.
@pytest.fixture(params=["mssql", "spark"])
def engine(request, database, spark_database):
    if request.param == "mssql":
        return SimpleNamespace(name=request.param, database=database)
    elif request.param == "spark":
        return SimpleNamespace(name=request.param, database=spark_database)
    else:
        assert False


def test_driver_in_container(run_in_container, engine):
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
            "test-connection",
            "--backend",
            backend,
            "--url",
            url,
        ]
    )
