import datetime

import hypothesis.strategies as st

from databuilder.query_model.nodes import (
    AggregateByPatient,
    Case,
    Filter,
    Function,
    PickOneRowPerPatient,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Sort,
    Value,
    node_types,
)
from tests.lib.query_model_utils import get_all_operations

# This module defines a set of recursive Hypothesis strategies for generating query model graphs.
#
# There are a few points where we deliberate order the types that we choose from, with the
# "simplest" first (by some subjective measure). This is to enable Hypothesis to more effectively
# explore the query space and to "shrink" examples when it finds errors. These points are commented
# below.
#
# We use several Hypothesis combinators for defining our strategies. Most (`one_of`, `just`,
# `sampled_from`) are fairly self-explanatory. A couple are worth clarifying.
#     * `st.builds()` is used to construct objects, it takes the class and strategies
#       corresponding to the constructor arguments.
#     * `@st.composite` allows us to define a strategy by composing other strategies with
#       arbitrary Python code; it adds a `draw` argument which is part of the machinery that
#       enables this composition but which doesn't form part of the signature of the resulting
#       strategy function.


def variable(patient_tables, event_tables, schema, value_strategies):
    # Every inner-function here returns a Hypothesis strategy for creating the thing it is named
    # for, not the thing itself.
    #
    # Several of these strategy functions ignore one or more of their arguments in order to make
    # them uniform with other functions that return the same sort of strategy. Such ignored
    # arguments are named with a leading underscore.

    # Series strategies
    #
    # Whenever a series is needed, we call series() passing the type of the series and frame that
    # it should be built on (these are either constrained by the context in which the series is to
    # be used or chosen arbitrarily by the caller).
    #
    # This strategy then chooses an arbitrary concrete series that respects the constraints imposed
    # by the passed type and frame.
    @st.composite
    def series(draw, type_, frame):
        class DomainConstraint:
            PATIENT = (True,)
            NON_PATIENT = (False,)
            ANY = (True, False)

        # Order matters: "simpler" first (see header comment)
        series_constraints = {
            value: ({int, float, bool, datetime.date}, DomainConstraint.PATIENT),
            select_column: ({int, float, bool, datetime.date}, DomainConstraint.ANY),
            eq: ({bool}, DomainConstraint.ANY),
            add: ({int, float}, DomainConstraint.ANY),
            count: ({int}, DomainConstraint.PATIENT),
        }
        series_types = series_constraints.keys()

        def constraints_match(series_type):
            type_constraint, domain_constraint = series_constraints[series_type]
            return (
                type_ in type_constraint
                and is_one_row_per_patient_frame(frame) in domain_constraint
            )

        possible_series = [s for s in series_types if constraints_match(s)]
        assert possible_series, f"No series matches {type_}, {type(frame)}"

        series_strategy = draw(st.sampled_from(possible_series))
        return draw(series_strategy(type_, frame))

    def value(type_, _frame):
        return st.builds(Value, value_strategies[type_])

    def select_column(type_, frame):
        column_names = [n for n, t in schema.column_types if t == type_]
        return st.builds(SelectColumn, st.just(frame), st.sampled_from(column_names))

    @st.composite
    def eq(draw, _type, frame):
        type_ = draw(any_type())
        lhs = draw(series(type_, draw(one_row_per_patient_frame_or(frame))))
        rhs = draw(series(type_, draw(one_row_per_patient_frame_or(frame))))
        return Function.EQ(lhs, rhs)

    @st.composite
    def add(draw, type_, frame):
        return Function.Add(
            draw(series(type_, draw(one_row_per_patient_frame_or(frame)))),
            draw(series(type_, draw(one_row_per_patient_frame_or(frame)))),
        )

    def count(_type, _frame):
        return st.builds(AggregateByPatient.Count, any_frame())

    def any_type():
        return st.sampled_from(list(value_strategies.keys()))

    # Frame strategies
    #
    # The main concern when choosing a frame is whether it has one or many rows per patient. Some
    # callers require one or the other, some don't mind; so we provide strategies for each case.
    # And sometimes callers need _either_ the frame they have in their hand _or_ an arbitrary
    # patient frame, so we provide a strategy for that too.
    #
    # At variance with the general approach here, many-rows-per-patient frames are created by
    # imperatively building stacks of filters on top of select nodes, rather than relying on
    # recursion, because it enormously simplifies the logic needed to keep filter conditions
    # consistent with the source.
    def any_frame():
        # Order matters: "simpler" first (see header comment)
        return st.one_of(one_row_per_patient_frame(), many_rows_per_patient_frame())

    def one_row_per_patient_frame():
        return select_patient_table()

    @st.composite
    def many_rows_per_patient_frame(draw):
        source = draw(select_table())
        for _ in range(draw(st.integers(min_value=0, max_value=6))):
            source = draw(filter_(source))
        return source

    def one_row_per_patient_frame_or(frame):
        if is_one_row_per_patient_frame(frame):
            return st.just(frame)
        # Order matters: "simpler" first (see header comment)
        return st.one_of(one_row_per_patient_frame(), st.just(frame))

    def select_table():
        return st.builds(SelectTable, st.sampled_from(event_tables), st.just(schema))

    def select_patient_table():
        return st.builds(
            SelectPatientTable, st.sampled_from(patient_tables), st.just(schema)
        )

    @st.composite
    def filter_(draw, source):
        condition = draw(series(bool, draw(ancestor_of(source))))
        return Filter(source, condition)

    @st.composite
    def ancestor_of(draw, frame):
        for _ in range(draw(st.integers(min_value=0, max_value=3))):
            if hasattr(frame, "source"):
                frame = frame.source
            else:
                break
        return frame

    # Variable strategy
    #
    # Puts everything above together to create a variable.
    @st.composite
    def valid_variable(draw):
        type_ = draw(any_type())
        frame = draw(one_row_per_patient_frame())
        return draw(series(type_, frame).filter(uses_the_database))

    return valid_variable()


# The second set is a temporary list of node types not covered by the new query generation approach.
known_missing_operations = {
    AggregateByPatient.CombineAsSet,
    Function.In,
    Function.StringContains,
} | {
    Case,
    Sort,
    PickOneRowPerPatient,
    AggregateByPatient.Max,
    AggregateByPatient.Min,
    AggregateByPatient.Exists,
    AggregateByPatient.Sum,
    Function.IsNull,
    Function.LE,
    Function.NE,
    Function.GT,
    Function.LT,
    Function.GE,
    Function.And,
    Function.Or,
    Function.Not,
    Function.Negate,
    Function.Subtract,
    Function.Multiply,
    Function.CastToFloat,
    Function.CastToInt,
    Function.YearFromDate,
    Function.MonthFromDate,
    Function.DayFromDate,
    Function.ToFirstOfYear,
    Function.ToFirstOfMonth,
    Function.DateAddYears,
    Function.DateAddMonths,
    Function.DateAddDays,
    Function.DateDifferenceInYears,
    Function.DateDifferenceInMonths,
    Function.DateDifferenceInDays,
}


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


def is_one_row_per_patient_frame(frame):
    return isinstance(frame, SelectPatientTable)
