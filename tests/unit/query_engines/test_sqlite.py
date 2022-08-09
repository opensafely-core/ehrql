import sqlalchemy

from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_model import (
    Function,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
    Value,
)

BOOLEAN_COLUMN = SelectColumn(SelectPatientTable("t", TableSchema(c=bool)), "c")


class DummyBackend:
    def get_table_expression(self, _name, _schema):
        return sqlalchemy.table("t", sqlalchemy.Column("c", sqlalchemy.Boolean))


def test_or_with_literal():
    # SQLAlchemy doesn't provide reverse bitwise operations, so `False | Column()` raises a `TypeError`.
    # See https://github.com/sqlalchemy/sqlalchemy/issues/5846.
    engine = SQLiteQueryEngine(None, DummyBackend())
    engine.get_sql(Function.Or(Value(True), BOOLEAN_COLUMN))
    engine.get_sql(Function.Or(BOOLEAN_COLUMN, Value(True)))


def test_and_with_literal():
    # SQLAlchemy doesn't provide reverse bitwise operations, so `True & Column()` raises a `TypeError`.
    # See https://github.com/sqlalchemy/sqlalchemy/issues/5846.
    engine = SQLiteQueryEngine(None, DummyBackend())
    engine.get_sql(Function.And(Value(False), BOOLEAN_COLUMN))
    engine.get_sql(Function.And(BOOLEAN_COLUMN, Value(False)))
