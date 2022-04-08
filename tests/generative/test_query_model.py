import os

import hypothesis as hyp
import hypothesis.strategies as st

from databuilder.query_model import TableSchema, Value

from ..lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
from . import data_setup, variable_strategies
from .conftest import count_nodes, observe_inputs

# To simplify data generation, all tables have the same schema.
schema = TableSchema(i1=int, i2=int, b1=bool, b2=bool)
patient_id_column, patient_tables, event_tables, Backend = data_setup.setup(
    schema, num_patient_tables=2, num_event_tables=2
)

# Use the same strategies for values both for query generation and data generation.
int_values = st.integers(min_value=0, max_value=10)
bool_values = st.booleans()

# And here are strategies for generating data. This is complicated by the need for patient ids in patient tables to
# be unique (see `patient_records()`).
max_patient_id = 10
max_num_patient_records = max_patient_id  # <= max_patient_id, hasn't been fine-tuned
max_num_event_records = max_patient_id  # could be anything, hasn't been fine-tuned


def record(table, id_strategy):
    # We don't construct the actual objects here because it's easier to extract stats for the generated data if we
    # pass around simple objects.
    columns = {patient_id_column: id_strategy}
    for name, type_ in schema.items():
        type_strategy = {int: int_values, bool: bool_values}[type_]
        columns[name] = type_strategy

    return st.builds(dict, type=st.just(table), **columns)


@st.composite
def concat(draw, *list_strategies):
    results = []
    for list_strategy in list_strategies:
        for example in draw(list_strategy):
            results.append(example)
    return results


patient_ids = st.integers(min_value=1, max_value=max_patient_id)


def event_records(table):
    return st.lists(
        record(table, patient_ids), min_size=1, max_size=max_num_event_records
    )


@st.composite
def patient_records(draw, table):
    # This strategy ensures that the patient ids are unique. We need to maintain the state to ensure that uniqueness
    # inside the strategy itself so that we can ensure the tests are idempotent as Hypothesis requires. That means that
    # this strategy must be called once only for a given table in a given test.
    used_ids = []

    @st.composite
    def one_patient_record(draw_):
        id_ = draw_(patient_ids)
        hyp.assume(id_ not in used_ids)
        used_ids.append(id_)
        return draw(record(table, st.just(id_)))

    return draw(
        st.lists(one_patient_record(), min_size=1, max_size=max_num_patient_records)
    )


def records():
    return concat(
        *[patient_records(t) for t in patient_tables],
        *[event_records(t) for t in event_tables]
    )


max_examples = int(os.environ.get("EXAMPLES", 100))

variable_strategy = variable_strategies.variable(
    [t.__tablename__ for t in patient_tables],
    [t.__tablename__ for t in event_tables],
    schema,
    int_values,
    bool_values,
)


@hyp.given(variable=variable_strategy, data=records())
@hyp.settings(
    max_examples=max_examples,
    deadline=None,
    suppress_health_check=[hyp.HealthCheck.filter_too_much],
)
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
        "population": Value(True),
        "v": variable,
    }

    run_with(InMemoryDatabase, InMemoryQueryEngine, instances, variables)


def run_with(database_class, engine_class, instances, variables):
    database = database_class()
    database.setup(instances)

    engine = engine_class(variables, Backend(database.host_url()))
    with engine.execute_query() as results:
        result = list(dict(row) for row in results)
        result.sort(key=lambda i: i["patient_id"])  # ensure stable ordering
        return result


def instantiate(data):
    return [item.pop("type")(**item) for item in data]
