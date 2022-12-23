import pytest

from databuilder.backends.tpp import TPPBackend
from databuilder.query_language import get_tables_from_namespace
from databuilder.tables.beta import tpp
from databuilder.utils.orm_utils import orm_classes_from_tables
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
    engine.setup(metadata=_tpp_orm_metadata())
    results = engine.extract(dataset)
    assert results == []


def _tpp_orm_metadata():
    # Return a SQLAlchemy MetaData object which contains references to all the tables in
    # the logical TPP schema (i.e. the schema we present in ehrQL)
    orm_classes = orm_classes_from_tables(
        table for _, table in get_tables_from_namespace(tpp)
    )
    first_orm_class = list(orm_classes.values())[0]
    return first_orm_class.metadata


def test_dataset_definition_against_tpp_backend(mssql_engine):
    # In contract to `_tpp_orm_metadata` above, this creates the schema as it actualy
    # exists in the TPP database, and therefore requires the `TPPBackend` to translate
    # it appropriately
    mssql_engine.setup(metadata=tpp_schema.Base.metadata)
    results = mssql_engine.extract(dataset, backend=TPPBackend())
    assert results == []
