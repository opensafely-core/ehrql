import datetime

import pytest
import sqlalchemy

from cohortextractor.query_engines import mssql


@pytest.mark.parametrize(
    "lst,size,expected",
    [
        ([], 10, []),
        (range(7), 3, [[0, 1, 2], [3, 4, 5], [6]]),
        (range(4), 6, [[0, 1, 2, 3]]),
        (range(12), 4, [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]),
    ],
)
def test_split_list_into_batches(lst, size, expected):
    lst = list(lst)
    results = mssql.split_list_into_batches(lst, size)
    results = list(results)
    assert results == expected


def test_mssql_date_types():
    # Note: it would be nice to parameterize this test, but given that the
    # inputs are SQLAlchemy expressions I don't know how to do this without
    # constructing the column objects outside of the test, which I don't really
    # want to do.
    date_col = sqlalchemy.Column("date_col", mssql.MSSQLDate())
    datetime_col = sqlalchemy.Column("datetime_col", mssql.MSSQLDateTime())
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
            dialect=mssql.MssqlQueryEngine.sqlalchemy_dialect.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
