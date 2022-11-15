import pytest

from databuilder.orm_utils import orm_classes_from_ql_table_namespace
from databuilder.tables.beta import tpp

from .dataset_definition import dataset


def test_dataset_definition(engine):
    if engine.name != "mssql":
        pytest.skip()

    orm_classes = orm_classes_from_ql_table_namespace(tpp)
    engine.setup(metadata=orm_classes.Base.metadata)
    results = engine.extract(dataset)
    for s in engine.dump_dataset_sql(dataset):
        print(s)
    assert results == []
