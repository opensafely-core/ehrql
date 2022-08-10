import hypothesis as hyp
import hypothesis.errors
import hypothesis.strategies as st

from databuilder.query_model import (
    AggregateByPatient,
    Filter,
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    ValidationError,
    Value,
    get_input_nodes,
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
            # See `sort`
            # pick_one_row_per_patient,
        )
    )

    many_rows_per_patient_frame = st.deferred(
        lambda: st.one_of(
            select_table,
            # See `sort`
            # sorted_frame,
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

    # See `sort`
    # sorted_frame = st.deferred(lambda: st.one_of(sort))

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
    select_column = qm_builds(SelectColumn, frame, st.sampled_from(list(schema.keys())))

    filter_ = qm_builds(Filter, many_rows_per_patient_frame, series)

    # TODO: gives inconsistent test results, see https://github.com/opensafely-core/databuilder/issues/461
    # sort = qm_builds(Sort, many_rows_per_patient_frame, many_rows_per_patient_series)

    # See `sort`
    # pick_one_row_per_patient = qm_builds(
    #     PickOneRowPerPatient,
    #     sorted_frame,
    #     st.sampled_from([Position.FIRST, Position.LAST]),
    # )

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
    not_ = qm_builds(Function.Not, series)

    is_null = qm_builds(Function.IsNull, series)

    negate = qm_builds(Function.Negate, series)
    add = qm_builds(Function.Add, series, series)
    subtract = qm_builds(Function.Subtract, series, series)

    # TODO Unsupported operations: everything that acts on dates or collections

    # Variables must be single values which have been reduced to the patient level. We also need to ensure that they
    # contains nodes which actually access the database so that the query engine can calculate a patient universe.
    return one_row_per_patient_series.filter(uses_the_database)


# A specialized version of st.builds() which cleanly rejects invalid Query Model objects.
@st.composite
def qm_builds(draw, type_, *arg_strategies):
    args = [draw(s) for s in arg_strategies]

    try:
        node = type_(*args)
    except ValidationError:
        raise hypothesis.errors.UnsatisfiedAssumption

    hyp.assume(not is_trivial(node))  # see long comment below
    return node


def uses_the_database(v):
    database_uses = [SelectPatientTable, SelectTable]
    return any(t in database_uses for t in node_types(v))


# SQlAlchemy does a certain amount of interpretation and optimization client-side. In particular in some cases where it
# can statically determine that the result of a function is constant, it replaces that function with the constant
# value. In extreme cases this may mean that the result of an entire query is completely determined client-side. In
# those cases our engine cannot determine the population for the dataset because it draws the patient universe from all
# tables used by the query -- and the query will use no tables.
#
# So we need to exclude such queries. This function detects function calls that SQLAlchemy will optimize away so that
# can avoid queries made up entirely of such things.
#
# Note that it is not sufficient to check that there is at least one non-trivial node in the tree because the collapse
# of trivial nodes lower down the tree can cause those higher up to become collapsible. For example this query reduces
# to `False`:
#
#     Function.And(
#         lhs=SelectColumn(
#             source=SelectPatientTable(name="p0"),
#             name="b1",
#         ),
#         rhs=Function.IsNull(source=Value(value=0)),
#     )
#
# The only way to detect cases like that would be to replicate SQLAlchemy's interpretation of the entire tree in order
# to check that the query is non-trivial.
#
# We therefore exclude all trivial nodes from the query. That means that there are realistic queries with trivial
# subtrees that we can't generate with these strategies. We could consider composing known-non-trivial subtrees with
# possibly-trivial subtrees as a future improvement to these strategies.
#
# And advantage to this approach is that we reject huge numbers of trivial queries that Hypothesis was otherwise
# inclined to generate, so the queries generally are rather more realistic.
def is_trivial(node):  # pragma: no cover
    if type(node) in [
        Function.Not,
        Function.IsNull,
        Function.Negate,
        Function.YearFromDate,
    ]:
        # Unary functions are completely determined if their input is a literal
        if isinstance(get_input_nodes(node)[0], Value):
            return True

    # Shortcut-able binary functions may be completely determined if one of their inputs is a literal
    if isinstance(node, Function.And):
        if any(n == Value(False) for n in get_input_nodes(node)):
            return True
    if isinstance(node, Function.Or):
        if any(n == Value(True) for n in get_input_nodes(node)):
            return True

    if type(node) in [
        Function.And,
        Function.Or,
        Function.EQ,
        Function.NE,
        Function.LT,
        Function.LE,
        Function.GT,
        Function.GE,
        Function.Add,
        Function.Subtract,
        Function.DateAddDays,
        Function.DateDifferenceInYears,
        Function.In,
    ]:
        # All binary functions are completely determined if all of their inputs are literals
        if all(isinstance(n, Value) for n in get_input_nodes(node)):
            return True

    if type(node) in [
        Function.Not,
        Function.IsNull,
        Function.Negate,
    ]:
        # Nested application of these unary functions is allowed by the type system, but never necessary
        if isinstance(get_input_nodes(node)[0], type(node)):
            return True

    if isinstance(node, Function.Subtract):
        # Subtracting a value from itself always returns zero
        left, right = get_input_nodes(node)
        if left == right:
            return True

    return False
