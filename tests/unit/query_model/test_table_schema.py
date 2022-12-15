import datetime

from databuilder.query_model.table_schema import Column, TableSchema


def test_table_schema_equality():
    t1 = TableSchema(i=Column(int))
    t2 = TableSchema(i=Column(int))
    t3 = TableSchema(j=Column(int))
    assert t1 == t2
    assert t1 != t3
    assert t1 != "a fish"


def test_table_schema_hash():
    t1 = TableSchema(i=Column(int))
    t2 = TableSchema(i=Column(int))
    d = {t1: "hello"}
    assert d[t2] == "hello"


def test_repr_roundtrip():
    schema = TableSchema(
        c1=Column(int),
        c2=Column(datetime.date),
    )

    assert eval(repr(schema)) == schema


def test_from_primitives():
    t1 = TableSchema.from_primitives(
        c1=int,
        c2=str,
    )
    t2 = TableSchema(
        c1=Column(int),
        c2=Column(str),
    )
    assert t1 == t2


def test_get_column_type():
    schema = TableSchema(i=Column(int))
    assert schema.get_column_type("i") is int


def test_column_names():
    schema = TableSchema(
        c1=Column(int),
        c2=Column(datetime.date),
    )
    assert schema.column_names == ["c1", "c2"]


def test_column_types():
    schema = TableSchema(
        c1=Column(int),
        c2=Column(datetime.date),
    )
    assert schema.column_types == [("c1", int), ("c2", datetime.date)]


def test_get_column_categories():
    schema = TableSchema(
        c1=Column(str, categories=("a", "b", "c")),
    )
    assert schema.get_column_categories("c1") == ("a", "b", "c")
