import pytest

from databuilder.backends.tpp import TPPBackend
from databuilder.tables.beta import tpp
from databuilder.utils.orm_utils import orm_classes_from_ql_table_namespace
from tests.lib import tpp_schema

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
    orm_classes = orm_classes_from_ql_table_namespace(tpp)
    engine.setup(metadata=orm_classes.Base.metadata)
    results = engine.extract(dataset)
    assert results == []


def test_dataset_definition_against_tpp_backend(request, engine):
    if engine.query_engine_class is not TPPBackend.query_engine_class:
        pytest.skip("TPPBackend is only designed for one query engine")

    engine.setup(metadata=tpp_schema.Base.metadata)
    results = engine.extract(dataset, backend=TPPBackend())
    assert results == []
