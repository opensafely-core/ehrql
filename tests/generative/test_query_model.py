import os

import hypothesis as hyp
import hypothesis.strategies as st

from databuilder.query_engines.sqlite import SQLiteQueryEngine
from databuilder.query_model import TableSchema

from ..lib.databases import InMemorySQLiteDatabase
from ..lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
from . import data_setup, data_strategies, variable_strategies
from .conftest import count_nodes, observe_inputs

# To simplify data generation, all tables have the same schema.
schema = TableSchema(i1=int, i2=int, b1=bool, b2=bool)
(
    patient_classes,
    event_classes,
    all_patients_query,
    sqla_metadata,
) = data_setup.setup(schema, num_patient_tables=2, num_event_tables=2)

# Use the same strategies for values both for query generation and data generation.
int_values = st.integers(min_value=0, max_value=10)
bool_values = st.booleans()


variable_strategy = variable_strategies.variable(
    [c.__tablename__ for c in patient_classes],
    [c.__tablename__ for c in event_classes],
    schema,
    int_values,
    bool_values,
)
data_strategy = data_strategies.data(
    patient_classes, event_classes, schema, int_values, bool_values
)
settings = dict(
    max_examples=(int(os.environ.get("EXAMPLES", 100))),
    deadline=None,
    suppress_health_check=[hyp.HealthCheck.filter_too_much, hyp.HealthCheck.too_slow],
)


@hyp.given(variable=variable_strategy, data=data_strategy)
@hyp.settings(**settings)
def test_query_model(variable, data):
    hyp.target(tune_qm_graph_size(variable))
    observe_inputs(variable, data)
    run_test(data, variable)


def tune_qm_graph_size(variable):
    target_size = 40  # seems to give a reasonable spread of query model graphs
    return -abs(target_size - count_nodes(variable))


def run_test(data, variable):
    instances = instantiate(data)
    variables = {
        "population": all_patients_query,
        "v": variable,
    }

    in_mem_results = run_with(
        InMemoryDatabase, InMemoryQueryEngine, instances, variables
    )
    sqlite_results = run_with(
        InMemorySQLiteDatabase, SQLiteQueryEngine, instances, variables
    )
    assert in_mem_results == sqlite_results


def run_with(database_class, engine_class, instances, variables):
    database = database_class()
    database.setup(instances, metadata=sqla_metadata)

    engine = engine_class(database.host_url())
    with engine.execute_query(variables) as results:
        result = list(dict(row) for row in results)
        result.sort(key=lambda i: i["patient_id"])  # ensure stable ordering
        return result


def instantiate(data):
    instances = []
    for item in data:
        item = item.copy()
        instances.append(item.pop("type")(**item))
    return instances
