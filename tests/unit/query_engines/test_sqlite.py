import sqlalchemy

from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_model import Function, SelectColumn, SelectPatientTable, Value


class DummyBackend:
    def get_table_expression(self, _name):
        return (
            sqlalchemy.select([sqlalchemy.Column("c")])
            .select_from(sqlalchemy.table("t"))
            .subquery()
        )


def test_or_with_literal():
    # SQLAlchemy doesn't provide reverse bitwise operations, so `False | Column()` raises a `TypeError`.
    # See https://github.com/sqlalchemy/sqlalchemy/issues/5846.
    engine = SQLiteQueryEngine(DummyBackend())
    engine.get_sql(Function.Or(Value(True), SelectColumn(SelectPatientTable("t"), "c")))
    engine.get_sql(Function.Or(SelectColumn(SelectPatientTable("t"), "c"), Value(True)))


def test_and_with_literal():
    # SQLAlchemy doesn't provide reverse bitwise operations, so `True & Column()` raises a `TypeError`.
    # See https://github.com/sqlalchemy/sqlalchemy/issues/5846.
    engine = SQLiteQueryEngine(DummyBackend())
    engine.get_sql(
        Function.And(Value(False), SelectColumn(SelectPatientTable("t"), "c"))
    )
    engine.get_sql(
        Function.And(SelectColumn(SelectPatientTable("t"), "c"), Value(False))
    )
