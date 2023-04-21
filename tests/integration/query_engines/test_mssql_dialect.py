import datetime

import pytest
import sqlalchemy

from ehrql.query_engines.mssql_dialect import MSSQLDialect


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


def test_enforces_minimum_server_version(mssql_engine, monkeypatch):
    monkeypatch.setattr(MSSQLDialect, "minimum_server_version", (999999,))
    with pytest.raises(RuntimeError, match=r"we require at least \(999999,\)"):
        mssql_engine.sqlalchemy_engine().connect()


def test_float_literals_have_correct_type(mssql_engine):
    # When using the `pymssql` driver without special float handling the "0.5" below
    # gets typed as a decimal and then the result of SUM gets typed as fixed precision
    # decimal.
    sum_literal = sqlalchemy.func.sum(0.5)
    # When added to a decimal of greater precision, the result gets rounded and ends up
    # being 0.8
    query = sqlalchemy.select(sum_literal + 0.25)
    with mssql_engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))
    # By explicitly casting floats in our custom dialect we can get the correct result
    assert results[0][0] == 0.75
