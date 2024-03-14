"""
All databases have limits and Hypothesis finds it quite easy to generate examples which
exceed these limts e.g. dates which extended beyond the range of representable dates or
queries which are so deeply nested they cause the query planner to overflow.

These aren't the kinds of problem we're interested in here: we're trying to find queries
of the kind a user might plausibly write which either trigger an error or return
incorrect results in a particular engine.

So below we capture the kinds of error we're going to ignore for the purposes of
generative testing.
"""

import enum
import re

import sqlalchemy.exc


class IgnoredError(enum.Enum):
    TOO_COMPLEX = enum.auto()
    ARITHMETIC_OVERFLOW = enum.auto()
    DATE_OVERFLOW = enum.auto()
    UNSUPPORTED_SQL = enum.auto()
    CONNECTION_ERROR = enum.auto()


IGNORED_ERRORS = {
    IgnoredError.TOO_COMPLEX: [
        # MSSQL can only accept 10 levels of CASE nesting. The variable strategy will sometimes
        # generate queries that exceed that limit.
        (
            sqlalchemy.exc.OperationalError,
            re.compile(".+Case expressions may only be nested to level 10.+"),
        ),
        # SQLite raises a parser stack overflow error if the variable strategy generates queries
        # that result in many nested queries
        (sqlalchemy.exc.OperationalError, re.compile(".+parser stack overflow")),
        # mssql raises this error when the number of identifiers and constants contained in a single
        # expression is > 65,535.
        # https://learn.microsoft.com/en-US/sql/relational-databases/errors-events/mssqlserver-8632-database-engine-error?view=sql-server-ver16
        # The variable strategy may produce this when it stacks many date operations on top of one
        # another.  It's unlikely a real query would produce this.
        (
            sqlalchemy.exc.OperationalError,
            re.compile(
                ".+Internal error: An expression services limit has been reached.+"
            ),
        ),
        # Trino also raises an error if the variable strategy generates queries
        # that result in many nested or too-long queries; again the many-date stacking seems to be the
        # main culprit
        (
            sqlalchemy.exc.DBAPIError,
            re.compile(
                ".+TrinoQueryError.+the query may have too many or too complex expressions.+"
            ),
        ),
        # Another Trino error that appears to be due to overly complex queries - in this case
        # when the variable strategy has many nested horizontal aggregations
        (
            sqlalchemy.exc.DBAPIError,
            re.compile(
                r".+TrinoQueryError.+Error compiling class: io\/trino\/\$gen\/JoinFilterFunction.+"
            ),
        ),
        (
            sqlalchemy.exc.ProgrammingError,
            re.compile(".+TrinoUserError.+QUERY_TEXT_TOO_LARGE.+"),
        ),
        (
            sqlalchemy.exc.DBAPIError,
            re.compile(r".+TrinoQueryError.+Query exceeded maximum columns.+"),
        ),
    ],
    IgnoredError.ARITHMETIC_OVERFLOW: [
        # MSSQL raises these errors if an operation results in an integer bigger than
        # the max INT value or a float outside of the max range
        # https://learn.microsoft.com/en-us/sql/t-sql/data-types/int-bigint-smallint-and-tinyint-transact-sql?view=sql-server-ver16
        # https://learn.microsoft.com/en-us/sql/t-sql/data-types/float-and-real-transact-sql?view=sql-server-ver16#remarks
        # https://github.com/opensafely-core/ehrql/issues/1034
        #
        # Arithmetic operations that result in an out-of-range int or float
        (
            sqlalchemy.exc.OperationalError,
            re.compile(
                ".+Arithmetic overflow error converting expression to data type [int|float].+"
            ),
        ),
        # Attempting to convert a valid float to an out-of-range int
        (
            sqlalchemy.exc.OperationalError,
            re.compile(".+Arithmetic overflow error for type int.+"),
        ),
        # Trino
        (
            sqlalchemy.exc.DBAPIError,
            re.compile(r".+TrinoQueryError.+Value \w+ exceeds MAX_INT.+"),
        ),
    ],
    IgnoredError.DATE_OVERFLOW: [
        # The variable strategy will sometimes result in date operations that construct
        # invalid dates (e.g. a large positive or negative integer in a DateAddYears operation
        # may result in a date with a year that is outside of the allowed range)
        # The different query engines report errors from out-of-range dates in different ways:
        #
        # MSSQL
        # DateAddYears, with an invalid calculated year
        (
            sqlalchemy.exc.OperationalError,
            re.compile(".+Cannot construct data type date.+"),
        ),
        # DateAddMonths, resulting in an invalid date
        (
            sqlalchemy.exc.OperationalError,
            re.compile(".+Adding a value to a 'date' column caused an overflow.+"),
        ),
        #
        # SQLite
        # Note the leading `-` below: ISO format doesn't handle BC dates, and BC dates don't
        # always have four year digits
        (ValueError, re.compile(r"Invalid isoformat string: '-\d+-\d\d-\d\d'")),
        # In-memory engine
        # DateAddYears, with an invalid calculated year
        (
            ValueError,
            re.compile("year -?\\d+ is out of range"),
        ),
        # DateAddDays, with a number of days out of the valid range
        (
            ValueError,
            re.compile("Number of days -?\\d+ is out of range"),
        ),
        # DateAddMonths, resulting in an invalid date
        (
            OverflowError,
            re.compile("date value out of range"),
        ),
        #
        # Trino
        (
            # Invalid date errors
            sqlalchemy.exc.NotSupportedError,
            re.compile(r".+Could not convert '.+' into the associated python type"),
        ),
    ],
    IgnoredError.UNSUPPORTED_SQL: [
        # MSSQL can't handle constant expressions (not just literals, any expression
        # which evaluates as a constant) in ORDER BY clauses. In theory we could
        # identify these ourselves and exclude them as they're always no-ops, but this
        # isn't worth the effort right now so we need to stop Hypothesis telling us
        # about this.
        (
            sqlalchemy.exc.OperationalError,
            re.compile(".*do not support constants as ORDER BY clause expressions"),
        ),
        (
            sqlalchemy.exc.OperationalError,
            re.compile(
                ".*do not support integer indices as ORDER BY clause expressions"
            ),
        ),
    ],
    IgnoredError.CONNECTION_ERROR: [
        # Sometimes we lose connection to the database server in a way that isn't
        # important and does not warrant the noise of failing the generative tests.
        # mssql
        (
            sqlalchemy.exc.OperationalError,
            re.compile(r".+Unexpected EOF from the server.+", re.DOTALL),
        ),
    ],
}


def get_ignored_error_type(e):
    for ignored_error_type, errors in IGNORED_ERRORS.items():
        for exception_type, exception_regex in errors:
            if type(e) == exception_type and exception_regex.match(str(e)):
                return ignored_error_type
