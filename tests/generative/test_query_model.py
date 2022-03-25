import os

import hypothesis as hyp
import hypothesis.errors
import hypothesis.strategies as st
import sqlalchemy
import sqlalchemy.orm

from databuilder.query_model import (
    AggregateByPatient,
    Filter,
    Function,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Sort,
    TableSchema,
    ValidationError,
    Value,
    has_many_rows_per_patient,
    has_one_row_per_patient,
)

from ..conftest import QueryEngineFixture
from ..lib.in_memory import InMemoryDatabase, InMemoryQueryEngine
from .conftest import count_nodes, observe_inputs

mapper_registry = sqlalchemy.orm.registry()
next_id = iter(range(1, 2**63)).__next__


def build_table(name, schema_, patient_id_column_):
    columns = [
        sqlalchemy.Column("Id", sqlalchemy.Integer, primary_key=True, default=next_id),
        sqlalchemy.Column(patient_id_column_, sqlalchemy.Integer),
    ]
    for col_name, type_ in schema_.items():
        sqla_type = {int: sqlalchemy.Integer, bool: sqlalchemy.Boolean}[type_]
        columns.append(sqlalchemy.Column(col_name, sqla_type))

    table = sqlalchemy.Table(name, mapper_registry.metadata, *columns)
    class_ = type(name, (object,), dict(__tablename__=name))
    mapper_registry.map_imperatively(class_, table)

    return class_


# A specialized version of st.builds() which cleanly rejects invalid Query Model objects.
@st.composite
def qm_builds(draw, type_, *arg_strategies):
    args = [draw(s) for s in arg_strategies]

    try:
        return type_(*args)
    except ValidationError:
        raise hypothesis.errors.UnsatisfiedAssumption


@st.composite
def composite_filter(draw, wrapped, predicate):
    # I believe that this should be equivalent to the following (which could then be inlined). However this
    # version discards fewer invalid examples and is noticeably faster, for reasons that I can't understand.
    #
    #     wrapped.filter(predicate)
    example = draw(wrapped)
    hyp.assume(predicate(example))
    return example


# Here follows a set of recursive strategies for constructing valid query model graphs.
#
# There is a set of strategies corresponding to the abstract types in the query model (for example `frame` or
# `one_row_per_patient_series`), each of which returns one of the direct subtypes of that type (both abstract and
# concrete). Another set of strategies corresponds to the concrete types in the query model (for example `filter` or
# `select_column`), each of which constructs the corresponding node and recursively invokes other strategies to
# provide the constructor arguments (using the strategy corresponding to the types of the arguments).
#
# So each concrete node type appears in two places: in its own strategy and in the strategy of its immediate
# supertype. And each abstract type appears in its own strategy, in the strategy of its immediate supertype and in
# the strategies of any concrete nodes which have a constructor argument of that abstract type.
#
# When we invoke the strategy of an abstract type, it tugs at a thread that runs down through the type hierarchy
# (picking a random subclass at each level) until it reaches a concrete type which can be constructed. (And it then
# does the same for all of the necessary constructor arguments.)
#
# The strategies are ordered in this file in the same order that the corresponding classes are defined in
# `query_model`, to make it easier to see the correspondence and to spot errors.
#
# There are, you will be astonished to learn, a few complications.
#
# * In order to help Hypothesis shrink the examples, the subclasses of each abstract type are ordered roughly by
#   "simplicity", using the number of child nodes as a heuristic. It's hard to follow even that, though, because of
#   the way the concrete types are grouped. And, partly as a consequence, this strategy doesn't shrink very well.
# * We need to use `st.deferred` in some places to allow (transitively) mutually recursive strategies. We're using it
#   in _all_ the abstract type strategies in order to allow us to keep the ordering the same as that of the definitions
#   in `query_model`.
# * The query model type hierarchy doesn't give us all the information we need, so the approach outlined above will
#   generate invalid query model graphs (due either to the domains or the types being incorrect). We handle this by
#   constructing the query model objects using a special-purpose strategy `qm_builds`, which can discard invalid
#   instances. There is an unexplored optimization avenue here: make the strategies more specific to include type
#   and/or domain, so that we don't discard so many examples.

frame = st.deferred(
    lambda: st.one_of(
        one_row_per_patient_frame,
        many_rows_per_patient_frame,
    )
)

series = st.deferred(
    lambda: st.one_of(
        unknown_dimension_series,
        definitely_one_row_patient_series,
        definitely_many_rows_per_patient_series,
    )
)

one_row_per_patient_frame = st.deferred(
    lambda: st.one_of(
        select_patient_table,
        pick_one_row_per_patient,
    )
)

many_rows_per_patient_frame = st.deferred(
    lambda: st.one_of(
        select_table,
        sorted_frame,
        filter_,
    )
)

one_row_per_patient_series = st.deferred(
    lambda: st.one_of(
        composite_filter(unknown_dimension_series, has_one_row_per_patient),
        definitely_one_row_patient_series,
    )
)

definitely_one_row_patient_series = st.deferred(
    lambda: st.one_of(
        value,
        exists,
        count_,
        # TODO: not supported by in-memory engine
        # min_,
        # TODO: not supported by in-memory engine
        # max_,
        sum_,
    )
)

many_rows_per_patient_series = st.deferred(
    lambda: st.one_of(
        composite_filter(unknown_dimension_series, has_many_rows_per_patient),
        definitely_many_rows_per_patient_series,
    )
)

# We don't currently have any examples of this type, but it's included here for consistency
# and to make it clear where it fits in.
definitely_many_rows_per_patient_series = st.deferred(lambda: st.one_of())

unknown_dimension_series = st.deferred(
    lambda: st.one_of(
        select_column,
        not_,
        is_null,
        negate,
        eq,
        ne,
        lt,
        le,
        gt,
        ge,
        and_,
        or_,
        add,
        subtract,
    )
)

sorted_frame = st.deferred(lambda: st.one_of(sort))

int_values = st.integers(min_value=0, max_value=10)
bool_values = st.booleans()
value = qm_builds(Value, st.one_of(int_values, bool_values))

# To simplify data generation, all tables have the same schema.
patient_id_column = "PatientId"
schema = TableSchema(i1=int, i2=int, b1=bool, b2=bool)
patient_tables = [build_table(name, schema, patient_id_column) for name in ["p1", "p2"]]
event_tables = [build_table(name, schema, patient_id_column) for name in ["e1", "e2"]]

select_table = qm_builds(
    SelectTable,
    st.sampled_from([t.__tablename__ for t in event_tables]),
    st.just(schema),
)
select_patient_table = qm_builds(
    SelectPatientTable,
    st.sampled_from([t.__tablename__ for t in patient_tables]),
    st.just(schema),
)
select_column = qm_builds(SelectColumn, frame, st.sampled_from(list(schema.keys())))

filter_ = qm_builds(Filter, many_rows_per_patient_frame, series)

sort = qm_builds(Sort, many_rows_per_patient_frame, series)

pick_one_row_per_patient = qm_builds(
    PickOneRowPerPatient, sorted_frame, st.sampled_from([Position.FIRST, Position.LAST])
)

exists = qm_builds(AggregateByPatient.Exists, many_rows_per_patient_frame)
count_ = qm_builds(AggregateByPatient.Count, many_rows_per_patient_frame)
# TODO: not supported by in-memory engine
# min_ = qm_builds(AggregateByPatient.Min, series)
# TODO: not supported by in-memory engine
# max_ = qm_builds(AggregateByPatient.Max, series)
sum_ = qm_builds(AggregateByPatient.Sum, many_rows_per_patient_series)

eq = qm_builds(Function.EQ, series, series)
ne = qm_builds(Function.NE, series, series)
lt = qm_builds(Function.LT, series, series)
le = qm_builds(Function.LE, series, series)
gt = qm_builds(Function.GT, series, series)
ge = qm_builds(Function.GE, series, series)

and_ = qm_builds(Function.And, series, series)
or_ = qm_builds(Function.Or, series, series)
not_ = qm_builds(Function.Not, series)

is_null = qm_builds(Function.IsNull, series)

negate = qm_builds(Function.Negate, series)
add = qm_builds(Function.Add, series, series)
subtract = qm_builds(Function.Subtract, series, series)

# TODO Unsupported operations: everything that acts on dates or collections

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
    return st.lists(record(table, patient_ids), max_size=max_num_event_records)


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

    return draw(st.lists(one_patient_record(), max_size=max_num_patient_records))


def records():
    return concat(
        *[patient_records(t) for t in patient_tables],
        *[event_records(t) for t in event_tables]
    )


max_examples = int(os.environ.get("EXAMPLES", 100))


@hyp.given(
    variable=one_row_per_patient_series,
    data=records(),
)
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
    instances = []
    for item in data:
        type_ = item.pop("type")
        instances.append(type_(**item))

    # We create an instance of the database for every test rather than using the standard fixture because Hypothesis
    # doesn't play nicely with function-scoped fixtures. That's not a problem for the in-memory database, but will
    # probably be too slow later when we come to use a real database. Some thought will be needed to make this work.
    engine = QueryEngineFixture("in_memory", InMemoryDatabase(), InMemoryQueryEngine)
    engine.setup(*instances)
    engine.extract_qm(
        {
            "population": Value(True),
            "v": variable,
        }
    )
