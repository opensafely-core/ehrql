from databuilder.query_model.table_schema import Column, TableSchema


def test_table_schema_equality():
    t1 = TableSchema(i=Column(int))
    t2 = TableSchema(i=Column(int))
    t3 = TableSchema(j=Column(int))
    assert t1 == t2
    assert t1 != t3
    assert t1 != "a fish"
