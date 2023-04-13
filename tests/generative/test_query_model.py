import datetime
import itertools
import os
import re

import hypothesis as hyp
import hypothesis.strategies as st
import pytest
import sqlalchemy.exc

from databuilder.dummy_data import DummyDataGenerator
from databuilder.query_model.nodes import (
    Column,
    Function,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
    Value,
)

from ..conftest import QUERY_ENGINE_NAMES, engine_factory
from . import data_setup, data_strategies, variable_strategies


IGNORE_RESULT = object()

# To simplify data generation, all tables have the same schema.
schema = TableSchema(
    i1=Column(int),
    i2=Column(int),
    b1=Column(bool),
    b2=Column(bool),
    d1=Column(datetime.date),
    d2=Column(datetime.date),
    f1=Column(float),
    f2=Column(float),
    s1=Column(str),
    s2=Column(str),
)
(
    patient_classes,
    event_classes,
    all_patients_query,
    sqla_metadata,
) = data_setup.setup(schema, num_patient_tables=2, num_event_tables=2)

# Use the same strategies for values both for query generation and data generation.
value_strategies = {
    int: st.integers(min_value=0, max_value=10),
    bool: st.booleans(),
    datetime.date: st.dates(
        min_value=datetime.date(2010, 1, 1), max_value=datetime.date(2020, 12, 31)
    ),
    float: st.floats(min_value=0.0, max_value=11.0, width=16, allow_infinity=False),
    str: st.text(alphabet=["a", "b", "c"], min_size=0, max_size=3),
}

variable_strategy = variable_strategies.variable(
    [c.__tablename__ for c in patient_classes],
    [c.__tablename__ for c in event_classes],
    schema,
    value_strategies,
)
data_strategy = data_strategies.data(
    patient_classes,
    event_classes,
    schema,
    value_strategies,
)
settings = dict(
    max_examples=(int(os.environ.get("GENTEST_EXAMPLES", 10))),
    deadline=None,
)


@pytest.fixture(scope="session")
def query_engines(request):
    # By contrast with the `engine` fixture which is parametrized over the types of
    # engine and so returns them one at a time, this fixture constructs and returns all
    # the engines together at once
    return {
        name: engine_factory(request, name, with_session_scope=True)
        for name in QUERY_ENGINE_NAMES
    }


@hyp.given(variable=variable_strategy, data=data_strategy)
@hyp.settings(**settings)
def test_query_model(query_engines, variable, data, recorder):
    recorder.record_inputs(variable, data)
    run_test(query_engines, data, variable, recorder)


@pytest.mark.parametrize(
    "operation,rhs",
    [
        (Function.DateAddYears, -2000),  # year=0
        (Function.DateAddYears, -3000),  # year=-1000
        (Function.DateAddYears, 8000),  # year = 10000
        (Function.DateAddMonths, -3000 * 12),
        (Function.DateAddMonths, 8000 * 12),
        (Function.DateAddDays, -3000 * 366),
        (Function.DateAddDays, 8000 * 366),
        (
            Function.DateAddDays,
            1500000000,
        ),  # triggers python overflow error with timedelta
    ],
)
def test_handle_date_errors(query_engines, operation, rhs):
    data = [
        {
            "type": data_setup.P0,
            "patient_id": 1,
            "d1": datetime.date(2000, 1, 1),
        }
    ]
    variable = operation(
        lhs=SelectColumn(
            source=SelectPatientTable(name="p0", schema=schema), name="d1"
        ),
        rhs=Value(rhs),
    )
    run_error_test(query_engines, data, variable)


def setup_test(data, variable):
    instances = instantiate(data)
    variables = {
        "population": all_patients_query,
        "v": variable,
    }
    return instances, variables


def run_test(query_engines, data, variable, recorder):
    instances, variables = setup_test(data, variable)

    # Test that we can successfully generate a minimal amount of dummy data
    dummy_data_generator = DummyDataGenerator(
        variables, population_size=1, batch_size=1, timeout=-1
    )
    assert len(dummy_data_generator.get_data()) > 0

    results = [
        (name, run_with(engine, instances, variables))
        for name, engine in query_engines.items()
    ]

    recorder.record_results(
        len(results), len([r for (_, r) in results if r is IGNORE_RESULT])
    )

    for first, second in itertools.combinations(results, 2):
        first_name, first_results = first
        second_name, second_results = second

        # Sometimes we hit test cases where one engine is known to have problems; skip them.
        if IGNORE_RESULT in [first_results, second_results]:
            continue  # pragma: no cover

        # If the results contain floats then we want only approximate equality to account
        # for rounding differences
        if any(
            isinstance(v, float)
            for res in [*first_results, *second_results]
            for v in res.values()
        ):
            for i, result in enumerate(first_results):
                assert result == pytest.approx(
                    second_results[i], rel=1e-5
                ), f"Mismatch between {first_name} and {second_name}"
        else:
            assert (
                first_results == second_results
            ), f"Mismatch between {first_name} and {second_name}"


def run_error_test(query_engines, data, variable):
    """
    Runs a test with input that is expected to raise an error in some way which is
    expected to be handled. If an exception is raised and handled within the test
    function, the result will be an `IGNORE_RESULT` object.  If the bad input is
    handled within the query engine itself, the result will contain a None value.
    e.g. attempting to add 8000 years to 2000-01-01 results in a date that is outside
    of the valid range (max 9999-12-31).  The sqlite engine returns None for this,
    all other engines raise an Exception that we catch and ignore.
    """
    instances, variables = setup_test(data, variable)
    for _, engine in query_engines.items():
        result = run_with(engine, instances, variables)
        assert result in [IGNORE_RESULT, [{"patient_id": 1, "v": None}]]


IGNORED_ERRORS = [
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
        re.compile(".+Internal error: An expression services limit has been reached.+"),
    ),
    # ARITHMETIC OVERFLOW ERRORS
    # mssql raises this error if an operation results in an integer bigger than the max INT value
    # or a float outside of the max range
    # https://learn.microsoft.com/en-us/sql/t-sql/data-types/int-bigint-smallint-and-tinyint-transact-sql?view=sql-server-ver16
    # https://learn.microsoft.com/en-us/sql/t-sql/data-types/float-and-real-transact-sql?view=sql-server-ver16#remarks
    # https://github.com/opensafely-core/databuilder/issues/1034
    (
        sqlalchemy.exc.OperationalError,
        re.compile(
            ".+Arithmetic overflow error converting expression to data type [int|float].+"
        ),
    ),  # arithmetic operations that result in an out-of-range int or floar
    (
        sqlalchemy.exc.OperationalError,
        re.compile(".+Arithmetic overflow error for type int.+"),
    ),  # attempting to convert a valid float to an out-of-range int
    #
    # OUT-OF-RANGE DATES
    # The variable strategy will sometimes result in date operations that construct
    # invalid dates (e.g. a large positive or negative integer in a DateAddYears operation
    # may result in a date with a year that is outside of the allowed range)
    # The different query engines report errors from out-of-range dates in different ways:
    # mssql
    (
        sqlalchemy.exc.OperationalError,
        re.compile(".+Cannot construct data type date.+"),
    ),  # DateAddYears, with an invalid calculated year
    (
        sqlalchemy.exc.OperationalError,
        re.compile(".+Adding a value to a 'date' column caused an overflow.+"),
    ),  # DateAddMonths, resulting in an invalid date
    # sqlite
    # Note the leading `-` below: ISO format doesn't handle BC dates, and BC dates don't
    # always have four year digits
    (ValueError, re.compile(r"Invalid isoformat string: '-\d+-\d\d-\d\d'")),
    # in-memory engine
    (
        ValueError,
        re.compile("year -?\\d+ is out of range"),
    ),  # DateAddYears, with an invalid calculated year
    (
        ValueError,
        re.compile("Number of days -?\\d+ is out of range"),
    ),  # DateAddDays, with a number of days out of the valid range
    (
        OverflowError,
        re.compile("date value out of range"),
    ),  # DateAddMonths, resulting in an invalid date
]


def run_with(engine, instances, variables):
    try:
        engine.setup(instances, metadata=sqla_metadata)
        return engine.extract_qm(variables)
    except Exception as e:  # pragma: no cover
        for ignored_error_type, ignored_error_regex in IGNORED_ERRORS:
            if type(e) == ignored_error_type and ignored_error_regex.match(str(e)):
                return IGNORE_RESULT
        raise
    finally:  # pragma: no cover
        engine.teardown()


def instantiate(data):
    instances = []
    for item in data:
        item = item.copy()
        instances.append(item.pop("type")(**item))
    return instances
