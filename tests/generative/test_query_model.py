import datetime
import itertools
import os
import re

import hypothesis as hyp
import hypothesis.strategies as st
import pytest
import sqlalchemy.exc

from databuilder.query_model.nodes import (
    Column,
    Function,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
    Value,
    count_nodes,
    node_types,
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
)
(
    patient_classes,
    event_classes,
    all_patients_query,
    sqla_metadata,
) = data_setup.setup(schema, num_patient_tables=2, num_event_tables=2)

# Use the same strategies for values both for query generation and data generation.
int_values = st.integers(min_value=0, max_value=10)
bool_values = st.booleans()
date_values = st.dates(
    min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31)
)
float_values = st.floats(min_value=0.0, max_value=11.0, width=16, allow_infinity=False)


variable_strategy = variable_strategies.variable(
    [c.__tablename__ for c in patient_classes],
    [c.__tablename__ for c in event_classes],
    schema,
    int_values,
    bool_values,
    date_values,
    float_values,
)
data_strategy = data_strategies.data(
    patient_classes,
    event_classes,
    schema,
    int_values,
    bool_values,
    date_values,
    float_values,
)
settings = dict(
    max_examples=(int(os.environ.get("GENTEST_EXAMPLES", 100))),
    deadline=None,
    suppress_health_check=[hyp.HealthCheck.filter_too_much, hyp.HealthCheck.too_slow],
)


@pytest.fixture(scope="session")
def query_engines(request):
    # By contrast with the `engine` fixture which is parametrized over the types of
    # engine and so returns them one at a time, this fixture constructs and returns all
    # the engines together at once
    return {
        name: engine_factory(request, name, with_session_scope=True)
        for name in QUERY_ENGINE_NAMES
        # The Spark engine is still too slow to run generative tests against
        if name != "spark"
    }


@hyp.given(variable=variable_strategy, data=data_strategy)
@hyp.settings(**settings)
def test_query_model(query_engines, variable, data, recorder):
    recorder.record_inputs(variable, data)
    tune_inputs(variable)
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
    ],
)
def test_handle_date_errors(query_engines, operation, rhs, recorder):
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


def tune_inputs(variable):
    # Encourage Hypothesis to maximize the number and type of nodes
    hyp.target(count_nodes(variable), label="number of nodes")
    hyp.target(len(node_types(variable)), label="number of node types")


def setup_test(data, variable):
    instances = instantiate(data)
    variables = {
        "population": all_patients_query,
        "v": variable,
    }
    return instances, variables


def run_test(query_engines, data, variable, recorder):
    instances, variables = setup_test(data, variable)

    results = [
        (name, run_with(engine, instances, variables))
        for name, engine in query_engines.items()
    ]

    recorder.record_results(
        len(results), len([r for r in results if r is IGNORE_RESULT])
    )

    for first, second in itertools.combinations(results, 2):
        first_name, first_results = first
        second_name, second_results = second

        # Sometimes we hit test cases where one engine is known to have problems; skip them.
        if IGNORE_RESULT in [first_results, second_results]:
            continue  # pragma: no cover

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
    # OUT-OF-RANGE DATES
    # The variable strategy will sometimes result in date operations that contruct
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
    (ValueError, re.compile("Couldn't parse date string")),
    # in-memory engine
    (
        ValueError,
        re.compile("year -?\\d+ is out of range"),
    ),  # DateAddYears, with an invalid calculated year
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
