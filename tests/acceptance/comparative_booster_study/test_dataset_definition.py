from databuilder.backends.tpp import TPPBackend
from databuilder.query_language import get_tables_from_namespace
from databuilder.tables.beta import tpp
from databuilder.utils.orm_utils import orm_classes_from_tables
from tests.lib import tpp_schema

from .dataset_definition import dataset


def test_dataset_definition(in_memory_engine):
    # Rapid test that the dataset definition can be evaluated without error
    in_memory_engine.setup(metadata=_tpp_orm_metadata())
    results = in_memory_engine.extract(dataset)
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
    # This test may not look like much but it confirms that the dataset definition can
    # be evaluated and compiled into valid SQL which runs without error against the TPP
    # schema via the TPP backend, so it's not quite as trivial as it looks
    mssql_engine.setup(metadata=tpp_schema.Base.metadata)
    results = mssql_engine.extract(dataset, backend=TPPBackend())
    assert results == []
