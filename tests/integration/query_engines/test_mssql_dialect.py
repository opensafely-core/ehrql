import datetime

import pytest
import sqlalchemy

from databuilder.query_engines.mssql_dialect import MSSQLDialect


def test_date_literals_have_correct_type(mssql_engine):
    case_statement = sqlalchemy.case(
        (
            sqlalchemy.literal(1) == 1,
            datetime.date(2000, 10, 5),
        ),
    )
    query = sqlalchemy.select(case_statement.label("output"))
    with mssql_engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))
    assert results[0].output == datetime.date(2000, 10, 5)


def test_casts_to_date():
    # This fails unless our MSSQL dialect sets the appropriate minimum server version.
    # By default it will treat DATE as an alias for DATETIME. See:
    # https://github.com/sqlalchemy/sqlalchemy/blob/rel_1_4_46/lib/sqlalchemy/dialects/mssql/base.py#L1623-L1627
    table = sqlalchemy.table("foo", sqlalchemy.Column("bar"))
    clause = sqlalchemy.cast(table.c.bar, sqlalchemy.Date)
    compiled = str(clause.compile(dialect=MSSQLDialect()))
    assert compiled == "CAST(foo.bar AS DATE)"


def test_enforces_minimum_server_version(mssql_engine, monkeypatch):
    monkeypatch.setattr(MSSQLDialect, "minimum_server_version", (999999,))
    with pytest.raises(RuntimeError, match=r"we require at least \(999999,\)"):
        mssql_engine.sqlalchemy_engine().connect()


def test_float_literals_have_correct_type(mssql_engine):
    sum_literal = sqlalchemy.func.sum(0.5)
    query = sqlalchemy.select(sum_literal + 0.25)
    with mssql_engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))
    assert results[0][0] == 0.75
