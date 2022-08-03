import pytest

from . import schema, tpp_schema
from .dataset_definition import dataset
from .tpp_backend import TPPBackend


def test_dataset_definition(engine):
    # This test may not look like much but it confirms that the database schema can be
    # created and that the dataset definition can be evaluated and compiled into valid
    # SQL which runs without error against that schema, so it's not quite as trivial as
    # it looks
    if engine.name == "spark":
        pytest.skip("spark tests are too slow")
    if engine.name == "sqlite":
        pytest.xfail("SQLite engine can't handle more than 64 variables")

    engine.setup(metadata=schema.Base.metadata)
    results = engine.extract(dataset)
    assert results == []


def test_dataset_definition_against_tpp_backend(request, engine):
    if engine.query_engine_class is not TPPBackend.query_engine_class:
        pytest.skip("TPPBackend is only designed for one query engine")

    engine.setup(metadata=tpp_schema.Base.metadata)
    # This is a workaroud for an awkwardness in our test setup process which I don't
    # have time to fix properly now. See:
    # https://github.com/opensafely-core/databuilder/issues/656
    request.addfinalizer(
        lambda: tpp_schema.Base.metadata.drop_all(engine.database.engine())
    )

    results = engine.extract(dataset, backend=TPPBackend())
    assert results == []
