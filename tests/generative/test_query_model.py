import datetime
import itertools
import os

import hypothesis as hyp
import hypothesis.strategies as st
import pytest
import sqlalchemy.exc

from databuilder.query_model.nodes import Column, TableSchema, count_nodes, node_types

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


variable_strategy = variable_strategies.variable(
    [c.__tablename__ for c in patient_classes],
    [c.__tablename__ for c in event_classes],
    schema,
    int_values,
    bool_values,
    date_values,
)
data_strategy = data_strategies.data(
    patient_classes, event_classes, schema, int_values, bool_values, date_values
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
    run_test(query_engines, data, variable)


def tune_inputs(variable):
    # Encourage Hypothesis to maximize the number and type of nodes
    hyp.target(count_nodes(variable), label="number of nodes")
    hyp.target(len(node_types(variable)), label="number of node types")


def run_test(query_engines, data, variable):
    instances = instantiate(data)
    variables = {
        "population": all_patients_query,
        "v": variable,
    }

    results = [
        (name, run_with(engine, instances, variables))
        for name, engine in query_engines.items()
    ]

    for first, second in itertools.combinations(results, 2):
        first_name, first_results = first
        second_name, second_results = second

        # Sometimes we hit test cases where one engine is known to have problems; skip them.
        if IGNORE_RESULT in [first_results, second_results]:
            continue  # pragma: no cover

        assert (
            first_results == second_results
        ), f"Mismatch between {first_name} and {second_name}"


def run_with(engine, instances, variables):
    try:
        engine.setup(instances, metadata=sqla_metadata)
        return engine.extract_qm(variables)
    except sqlalchemy.exc.OperationalError as e:  # pragma: no cover
        # MSSQL can only accept 10 levels of CASE nesting. The variable strategy will sometimes
        # generate queries that exceed that limit.
        if "Case expressions may only be nested to level 10" in str(e):
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
