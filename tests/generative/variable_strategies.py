import hypothesis.errors
import hypothesis.strategies as st

from databuilder.query_model.nodes import (
    AggregateByPatient,
    Case,
    Filter,
    Function,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Sort,
    ValidationError,
    Value,
    has_many_rows_per_patient,
    has_one_row_per_patient,
    node_types,
)

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
from tests.lib.query_model_utils import get_all_operations


def variable(patient_tables, event_tables, schema, int_values, bool_values):
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
            unknown_dimension_series.filter(has_one_row_per_patient),
            definitely_one_row_patient_series,
        )
    )

    definitely_one_row_patient_series = st.deferred(
        lambda: st.one_of(
            value,
            exists,
            count_,
            min_,
            max_,
            sum_,
        )
    )

    many_rows_per_patient_series = st.deferred(
        lambda: st.one_of(
            unknown_dimension_series.filter(has_many_rows_per_patient),
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

    value = qm_builds(Value, st.one_of(int_values, bool_values))

    select_table = qm_builds(
        SelectTable,
        st.sampled_from(event_tables),
        st.just(schema),
    )
    select_patient_table = qm_builds(
        SelectPatientTable,
        st.sampled_from(patient_tables),
        st.just(schema),
    )
    select_column = qm_builds(
        SelectColumn, frame, st.sampled_from(list(schema.column_names))
    )

    filter_ = qm_builds(Filter, many_rows_per_patient_frame, series)

    sort = qm_builds(Sort, many_rows_per_patient_frame, many_rows_per_patient_series)

    pick_one_row_per_patient = qm_builds(
        PickOneRowPerPatient,
        sorted_frame,
        st.sampled_from([Position.FIRST, Position.LAST]),
    )

    exists = qm_builds(AggregateByPatient.Exists, many_rows_per_patient_frame)
    count_ = qm_builds(AggregateByPatient.Count, many_rows_per_patient_frame)
    min_ = qm_builds(AggregateByPatient.Min, series)
    max_ = qm_builds(AggregateByPatient.Max, series)
    sum_ = qm_builds(AggregateByPatient.Sum, many_rows_per_patient_series)

    eq = qm_builds(Function.EQ, series, series)
    ne = qm_builds(Function.NE, series, series)
    lt = qm_builds(Function.LT, series, series)
    le = qm_builds(Function.LE, series, series)
    gt = qm_builds(Function.GT, series, series)
    ge = qm_builds(Function.GE, series, series)

    and_ = qm_builds(Function.And, series, series)
    or_ = qm_builds(Function.Or, series, series)
    not_ = qm_builds(Function.Not, series, avoided_inputs=[Function.Not])

    never_null = [
        Function.IsNull,
        AggregateByPatient.Exists,
        AggregateByPatient.Count,
        AggregateByPatient.Min,
        AggregateByPatient.Max,
        AggregateByPatient.Sum,
    ]
    is_null = qm_builds(Function.IsNull, series, avoided_inputs=never_null)

    negate = qm_builds(Function.Negate, series, avoided_inputs=[Function.Negate])
    add = qm_builds(Function.Add, series, series)
    subtract = qm_builds(Function.Subtract, series, series)

    assert_complete_coverage()

    # Variables must be single values which have been reduced to the patient level. We also need to ensure that they
    # contains nodes which actually access the database so that the query engine can calculate a patient universe.
    return one_row_per_patient_series.filter(uses_the_database)


def carefully_draw(draw, strategy, avoided_types):
    if not avoided_types:
        return draw(strategy)
    while True:
        o = draw(strategy)
        if not any(isinstance(o, type_) for type_ in avoided_types):
            return o


# A specialized version of st.builds() which cleanly rejects invalid Query Model objects.
# We also record the QM operations for which strategies have been created and then assert that
# this includes all operations that exist, to act as a reminder to us to add new operations here
# when they are added to the query model.
def qm_builds(type_, *arg_strategies, avoided_inputs=None):
    included_operations.add(type_)

    @st.composite
    def strategy(draw, type_, *arg_strategies):
        args = [carefully_draw(draw, s, avoided_inputs) for s in arg_strategies]

        try:
            return type_(*args)
        except ValidationError:
            raise hypothesis.errors.UnsatisfiedAssumption

    return strategy(type_, *arg_strategies)


included_operations = set()

known_missing_operations = {
    AggregateByPatient.CombineAsSet,
    Case,
    Function.In,
    Function.StringContains,
    Function.CastToFloat,
    Function.CastToInt,
    Function.DateAddYears,
    Function.DateAddMonths,
    Function.DateAddDays,
    Function.YearFromDate,
    Function.MonthFromDate,
    Function.DayFromDate,
    Function.DateDifferenceInYears,
    Function.DateDifferenceInMonths,
    Function.DateDifferenceInDays,
    Function.ToFirstOfYear,
    Function.ToFirstOfMonth,
}


def assert_complete_coverage():
    assert_includes_all_operations(included_operations)


def assert_includes_all_operations(operations):  # pragma: no cover
    all_operations = set(get_all_operations())

    unexpected_missing = all_operations - known_missing_operations - operations
    assert (
        not unexpected_missing
    ), f"unseen operations: {[o.__name__ for o in unexpected_missing]}"

    unexpected_present = known_missing_operations & operations
    assert (
        not unexpected_present
    ), f"unexpectedly seen operations: {[o.__name__ for o in unexpected_present]}"


def uses_the_database(v):
    database_uses = [SelectPatientTable, SelectTable]
    return any(t in database_uses for t in node_types(v))
