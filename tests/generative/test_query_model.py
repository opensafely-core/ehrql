import datetime
import os
import re

import hypothesis as hyp
import hypothesis.strategies as st
import pytest
import sqlalchemy.exc

from ehrql.dummy_data import DummyDataGenerator
from ehrql.query_model.introspection import all_unique_nodes
from ehrql.query_model.nodes import (
    AggregateByPatient,
    Column,
    Function,
    Parameter,
    SelectColumn,
    SelectPatientTable,
    TableSchema,
    Value,
    get_series_type,
)
from tests.lib.query_model_utils import get_all_operations

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

population_strategy, variable_strategy = variable_strategies.population_and_variable(
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
    derandomize=not os.environ.get("GENTEST_RANDOMIZE"),
)

ENGINE_CONFIG = {
    # Exercise the codepath which writes to the temporary database as this is more
    # convoluted and thus, presumably, more prone to bugs
    "mssql": {"TEMP_DATABASE_NAME": "temp_tables"},
}


SELECTED_QUERY_ENGINES = (
    os.environ.get("GENTEST_QUERY_ENGINES", "").split() or QUERY_ENGINE_NAMES
)


@pytest.fixture(scope="session")
def query_engines(request):
    # By contrast with the `engine` fixture which is parametrized over the types of
    # engine and so returns them one at a time, this fixture constructs and returns all
    # the engines together at once
    return {
        name: engine_factory(request, name, with_session_scope=True)
        for name in SELECTED_QUERY_ENGINES
    }


# This is "meta test" i.e. a test of our test generating strategy, rather than a test of
# the system _using_ the test strategy. We want to ensure that we don't add new query
# model nodes without adding an appropriate strategy for them.
def test_variable_strategy_is_comprehensive():
    operations_seen = set()

    # This uses a fixed seed and no example database to make it deterministic
    @hyp.settings(max_examples=150, database=None, deadline=None)
    @hyp.seed(123456)
    @hyp.given(variable=variable_strategy)
    def record_operations_seen(variable):
        operations_seen.update(type(node) for node in all_unique_nodes(variable))

    record_operations_seen()

    known_missing_operations = {
        AggregateByPatient.CombineAsSet,
        # Parameters don't themselves form part of valid queries: they are placeholders
        # which must all be replaced with Values before the query can be executed.
        Parameter,
    }
    all_operations = set(get_all_operations())
    unexpected_missing = all_operations - known_missing_operations - operations_seen
    unexpected_present = known_missing_operations & operations_seen

    assert not unexpected_missing, f"unseen operations: {unexpected_missing}"
    assert not unexpected_present, f"unexpectedly seen operations: {unexpected_present}"


@hyp.given(
    population=population_strategy, variable=variable_strategy, data=data_strategy
)
@hyp.settings(**settings)
def test_query_model(query_engines, population, variable, data, recorder):
    recorder.record_inputs(variable, data)
    run_dummy_data_test(population, variable)
    run_test(query_engines, data, population, variable, recorder)
    # We run the test again using a simplified population definition which includes all
    # patients: this ensures that the calculated value of `variable` matches for all
    # patients, not just those included in the original population (which may be zero,
    # if `data` happens not to contain any matching patients)
    run_test(query_engines, data, all_patients_query, variable, recorder)


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


def setup_test(data, population, variable):
    instances = instantiate(data)
    variables = {
        "population": population,
        "v": variable,
    }
    return instances, variables


def run_test(query_engines, data, population, variable, recorder):
    instances, variables = setup_test(data, population, variable)

    all_results = [
        (name, run_with(engine, instances, variables))
        for name, engine in query_engines.items()
    ]
    # Sometimes we hit test cases where one engine is known to have problems so we
    # ignore those results
    results = [(name, rows) for name, rows in all_results if rows is not IGNORE_RESULT]
    recorder.record_results(len(all_results), len(all_results) - len(results))

    # If we hit a case which _no_ database can handle (e.g. some silly bit of date
    # arithmetic results in an out-of-bounds date) then just bail out
    if not results:  # pragma: no cover
        return

    # Use the first engine's results as the baseline (this is arbitrary, equality being
    # transitive)
    first_name, first_results = results[0]
    # If the results contain floats then we want only approximate equality to account
    # for rounding differences
    if any(get_series_type(v) is float for v in variables.values()):
        first_results = [pytest.approx(row, rel=1e-5) for row in first_results]

    for other_name, other_results in results[1:]:
        assert (
            first_results == other_results
        ), f"Mismatch between {first_name} and {other_name}"


def run_dummy_data_test(population, variable):
    # We can't do much more here than check that the generator runs without error, but
    # that's enough to catch quite a few issues
    dummy_data_generator = DummyDataGenerator(
        {"population": population, "v": variable},
        population_size=1,
        # We need a batch size bigger than one otherwise by chance (or, more strictly,
        # by deterministic combination of query and fixed random seed) we can end up
        # generating no examples of any tables, resulting in a not very interesting
        # failure mode.
        batch_size=5,
        timeout=-1,
    )
    assert isinstance(dummy_data_generator.get_data(), list)
    # Using a simplified population definition which should always have matching patients
    # we can confirm that we generate at least some data
    dummy_data_generator = DummyDataGenerator(
        {"population": all_patients_query, "v": variable},
        population_size=1,
        batch_size=1,
        timeout=-1,
    )
    assert len(dummy_data_generator.get_data()) > 0


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
    instances, variables = setup_test(data, all_patients_query, variable)
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
    # ARITHMETIC OVERFLOW ERRORS
    # mssql raises this error if an operation results in an integer bigger than the max INT value
    # or a float outside of the max range
    # https://learn.microsoft.com/en-us/sql/t-sql/data-types/int-bigint-smallint-and-tinyint-transact-sql?view=sql-server-ver16
    # https://learn.microsoft.com/en-us/sql/t-sql/data-types/float-and-real-transact-sql?view=sql-server-ver16#remarks
    # https://github.com/opensafely-core/ehrql/issues/1034
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
    # Trino
    (
        # Invalid date errors
        sqlalchemy.exc.NotSupportedError,
        re.compile(r".+Could not convert '.+' into the associated python type"),
    ),
]


def run_with(engine, instances, variables):
    try:
        engine.setup(instances, metadata=sqla_metadata)
        return engine.extract_qm(
            variables,
            config=ENGINE_CONFIG.get(engine.name, {}),
        )
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
