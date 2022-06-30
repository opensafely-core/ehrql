import pytest

from . import schema
from .dataset_definition import dataset


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
