import datetime

import pytest
import sqlalchemy

from cohortextractor2 import sqlalchemy_types
from cohortextractor2.query_engines.mssql_dialect import MSSQLDialect


def test_mssql_date_types():
    # Note: it would be nice to parameterize this test, but given that the
    # inputs are SQLAlchemy expressions I don't know how to do this without
    # constructing the column objects outside of the test, which I don't really
    # want to do.
    date_col = sqlalchemy.Column("date_col", sqlalchemy_types.Date())
    datetime_col = sqlalchemy.Column("datetime_col", sqlalchemy_types.DateTime())
    assert _str(date_col > "2021-08-03") == "date_col > '20210803'"
    assert _str(datetime_col < "2021-03-23") == "datetime_col < '2021-03-23T00:00:00'"
    assert _str(date_col == datetime.date(2021, 5, 15)) == "date_col = '20210515'"
    assert (
        _str(datetime_col == datetime.datetime(2021, 5, 15, 9, 10, 0))
        == "datetime_col = '2021-05-15T09:10:00'"
    )
    assert _str(date_col == None) == "date_col IS NULL"  # noqa: E711
    assert _str(datetime_col == None) == "datetime_col IS NULL"  # noqa: E711
    with pytest.raises(ValueError):
        _str(date_col > "2021")
    with pytest.raises(ValueError):
        _str(datetime_col == "2021-08")
    with pytest.raises(TypeError):
        _str(date_col > 2021)
    with pytest.raises(TypeError):
        _str(datetime_col == 2021)


def _str(expression):
    return str(
        expression.compile(
            dialect=MSSQLDialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
