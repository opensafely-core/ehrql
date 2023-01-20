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
    #
    # A note on frames and domains:
    #
    #     When we pass `frame` as an argument to a series strategy function, the intended semantics
    #     are always "construct a series that is _consistent_ with this frame". It's always
    #     permitted to return a one-row-per-patient series, because such series can always be
    #     composed a many-rows-per-patient series; so there are series strategy functions that,
    #     always or sometimes, ignore the frame argument.
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
            exists: ({bool}, DomainConstraint.PATIENT),
            count: ({int}, DomainConstraint.PATIENT),
            is_null: ({bool}, DomainConstraint.ANY),
            not_: ({bool}, DomainConstraint.ANY),
            year_from_date: ({int}, DomainConstraint.ANY),
            month_from_date: ({int}, DomainConstraint.ANY),
            day_from_date: ({int}, DomainConstraint.ANY),
            to_first_of_year: ({datetime.date}, DomainConstraint.ANY),
            to_first_of_month: ({datetime.date}, DomainConstraint.ANY),
            negate: ({int, float}, DomainConstraint.ANY),
            eq: ({bool}, DomainConstraint.ANY),
            ne: ({bool}, DomainConstraint.ANY),
            and_: ({bool}, DomainConstraint.ANY),
            or_: ({bool}, DomainConstraint.ANY),
            lt: ({bool}, DomainConstraint.ANY),
            gt: ({bool}, DomainConstraint.ANY),
            le: ({bool}, DomainConstraint.ANY),
            ge: ({bool}, DomainConstraint.ANY),
            add: ({int, float}, DomainConstraint.ANY),
            subtract: ({int, float}, DomainConstraint.ANY),
            multiply: ({int, float}, DomainConstraint.ANY),
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

    def exists(_type, _frame):
        return st.builds(AggregateByPatient.Exists, any_frame())

    def count(_type, _frame):
        return st.builds(AggregateByPatient.Count, any_frame())

    @st.composite
    def is_null(draw, _type, frame):
        type_ = draw(any_type())
        return Function.IsNull(
            draw(series(type_, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def not_(draw, type_, frame):
        return Function.Not(
            draw(series(type_, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def year_from_date(draw, _type, frame):
        return Function.YearFromDate(
            draw(series(datetime.date, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def month_from_date(draw, _type, frame):
        return Function.MonthFromDate(
            draw(series(datetime.date, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def day_from_date(draw, _type, frame):
        return Function.DayFromDate(
            draw(series(datetime.date, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def to_first_of_year(draw, _type, frame):
        return Function.ToFirstOfYear(
            draw(series(datetime.date, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def to_first_of_month(draw, _type, frame):
        return Function.ToFirstOfMonth(
            draw(series(datetime.date, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def negate(draw, type_, frame):
        return Function.Negate(
            draw(series(type_, draw(one_row_per_patient_frame_or(frame))))
        )

    @st.composite
    def eq(draw, _type, frame):
        type_ = draw(any_type())
        return draw(binary_operation(type_, frame, Function.EQ))

    @st.composite
    def ne(draw, _type, frame):
        type_ = draw(any_type())
        return draw(binary_operation(type_, frame, Function.NE))

    @st.composite
    def and_(draw, type_, frame):
        return draw(binary_operation(type_, frame, Function.And))

    @st.composite
    def or_(draw, type_, frame):
        return draw(binary_operation(type_, frame, Function.Or))

    @st.composite
    def lt(draw, _type, frame):
        type_ = draw(comparable_type())
        return draw(binary_operation(type_, frame, Function.LT))

    @st.composite
    def gt(draw, _type, frame):
        type_ = draw(comparable_type())
        return draw(binary_operation(type_, frame, Function.GT))

    @st.composite
    def le(draw, _type, frame):
        type_ = draw(comparable_type())
        return draw(binary_operation(type_, frame, Function.LE))

    @st.composite
    def ge(draw, _type, frame):
        type_ = draw(comparable_type())
        return draw(binary_operation(type_, frame, Function.GE))

    @st.composite
    def add(draw, type_, frame):
        return draw(binary_operation(type_, frame, Function.Add))

    @st.composite
    def subtract(draw, type_, frame):
        return draw(binary_operation(type_, frame, Function.Subtract))

    @st.composite
    def multiply(draw, type_, frame):
        return draw(binary_operation(type_, frame, Function.Multiply))

    @st.composite
    def binary_operation(draw, type_, frame, operator_func):
        # A strategy for operations that take lhs and rhs arguments of the
        # same type
        lhs = draw(series(type_, draw(one_row_per_patient_frame_or(frame))))
        rhs = draw(series(type_, draw(one_row_per_patient_frame_or(frame))))
        return operator_func(lhs, rhs)

    def any_type():
        return st.sampled_from(list(value_strategies.keys()))

    def comparable_type():
        return st.sampled_from(list(set(value_strategies.keys()) - {bool}))

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
    AggregateByPatient.Sum,
    Function.CastToFloat,
    Function.CastToInt,
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
