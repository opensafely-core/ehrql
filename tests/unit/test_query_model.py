import datetime
from collections.abc import Set
from types import SimpleNamespace
from typing import Any

import pytest

from databuilder.query_model import (
    AggregateByPatient,
    Case,
    DomainMismatchError,
    Filter,
    Frame,
    Function,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    Series,
    Sort,
    TableSchema,
    TypeValidationError,
    Value,
    get_domain,
    get_series_type,
    has_one_row_per_patient,
)

EVENTS_SCHEMA = TableSchema(date=datetime.date, code=str, flag=bool)


# TEST BASIC QUERY MODEL PROPERTIES
#


@pytest.fixture
def queries():
    q = SimpleNamespace()

    patients = SelectPatientTable("patients", TableSchema(sex=str))
    events = SelectTable("events", EVENTS_SCHEMA)
    code = SelectColumn(events, "code")
    date = SelectColumn(events, "date")
    vaccinations = Filter(events, Function.EQ(code, Value("abc123")))
    anaphylaxis_events = Filter(
        events, Function.In(code, Value(frozenset({"def456", "xyz789"})))
    )

    q.sex = SelectColumn(patients, "sex")
    q.vaccination_count = AggregateByPatient.Count(vaccinations)
    q.first_vaccination = PickOneRowPerPatient(Sort(vaccinations, date), Position.FIRST)
    q.vaccination_status = Case(
        {
            Function.EQ(q.vaccination_count, Value(1)): Value("partial"),
            Function.EQ(q.vaccination_count, Value(2)): Value("full"),
            Function.GE(q.vaccination_count, Value(3)): Value("boosted"),
        },
        default=Value("unvaccinated"),
    )

    q.vaccination_days = SelectColumn(vaccinations, "date")
    q.vaccination_days_set = AggregateByPatient.CombineAsSet(q.vaccination_days)
    q.anaphylaxis_co_occurance = Filter(
        anaphylaxis_events, Function.In(date, q.vaccination_days_set)
    )
    q.had_anaphylaxis = AggregateByPatient.Exists(q.anaphylaxis_co_occurance)

    return q


def test_queries_have_expected_types(queries):
    assert isinstance(queries.sex, Series)
    assert isinstance(queries.vaccination_count, Series)
    assert isinstance(queries.first_vaccination, Frame)
    assert isinstance(queries.vaccination_status, Series)
    assert isinstance(queries.vaccination_days, Series)
    assert isinstance(queries.vaccination_days_set, Series)
    assert isinstance(queries.anaphylaxis_co_occurance, Frame)
    assert isinstance(queries.had_anaphylaxis, Series)


def test_queries_have_expected_dimension(queries):
    assert has_one_row_per_patient(queries.sex)
    assert has_one_row_per_patient(queries.vaccination_count)
    assert has_one_row_per_patient(queries.first_vaccination)
    assert has_one_row_per_patient(queries.vaccination_status)
    assert not has_one_row_per_patient(queries.vaccination_days)
    assert has_one_row_per_patient(queries.vaccination_days_set)
    assert not has_one_row_per_patient(queries.anaphylaxis_co_occurance)
    assert has_one_row_per_patient(queries.had_anaphylaxis)


def test_series_contain_expected_types(queries):
    assert get_series_type(queries.sex) == str
    assert get_series_type(queries.vaccination_count) == int
    assert get_series_type(queries.vaccination_status) == str
    assert get_series_type(queries.vaccination_days) == datetime.date
    assert get_series_type(queries.vaccination_days_set) == Set[datetime.date]
    assert get_series_type(queries.had_anaphylaxis) == bool


def test_queries_are_hashable(queries):
    for query in vars(queries).values():
        assert hash(query) is not None


# We don't _have_ to maintain this property, but it's quite a convenient one to have and
# if we're going to break it then let's at least do so deliberately
def test_query_reprs_round_trip(queries):
    # This relies on all public query model names being imported into local scope
    for query in vars(queries).values():
        assert eval(repr(query)) == query


# TEST DOMAIN VALIDATION
#

# The simple, happy case: combining series derived directly from the same frame
def test_combining_series_from_same_frame_is_ok():
    events = SelectTable("events", TableSchema(value_1=int, value_2=int))
    value_1 = SelectColumn(events, "value_1")
    value_2 = SelectColumn(events, "value_2")
    assert Function.GT(value_1, value_2)


# We can also combine with a one-row-per-patient series derived from a different frame
# because we know we can always join by patient_id
def test_combining_a_patient_level_series_from_a_different_frame_is_ok():
    events = SelectTable("events", EVENTS_SCHEMA)
    vaccinations = SelectTable("vaccinations", EVENTS_SCHEMA)
    event_date = SelectColumn(events, "date")
    vaccination_date = SelectColumn(vaccinations, "date")
    # This makes a one-row-per-patient series which can be combined arbitrarily with
    # other series
    first_event_date = AggregateByPatient.Min(event_date)
    assert Function.EQ(first_event_date, vaccination_date)


# But we can't combine many-rows-per-patient series derived from different frames
def test_combining_non_patient_level_series_from_different_frames_throws_error():
    events = SelectTable("events", EVENTS_SCHEMA)
    vaccinations = SelectTable("vaccinations", EVENTS_SCHEMA)
    event_date = SelectColumn(events, "date")
    vaccination_date = SelectColumn(vaccinations, "date")
    with pytest.raises(DomainMismatchError):
        Function.EQ(event_date, vaccination_date)


# And in particular, we can't filter a Frame using a predicate (boolean Series) derived
# from a different Frame
def test_filtering_one_frame_by_a_condition_derived_from_another_throws_error():
    events = SelectTable("events", EVENTS_SCHEMA)
    vaccinations = SelectTable("vaccinations", EVENTS_SCHEMA)
    vaccine_code = SelectColumn(vaccinations, "code")
    filter_condition = Function.EQ(vaccine_code, Value("abc123"))
    with pytest.raises(DomainMismatchError):
        Filter(events, filter_condition)


# And ditto for sort
def test_sorting_one_frame_by_a_series_derived_from_another_throws_an_error():
    events = SelectTable("events", EVENTS_SCHEMA)
    vaccinations = SelectTable("vaccinations", EVENTS_SCHEMA)
    vaccine_code = SelectColumn(vaccinations, "code")
    with pytest.raises(DomainMismatchError):
        Sort(events, vaccine_code)


# We also can't combine results derived from the same source table if they've been
# through divergent filter operations. Although such operations aren't *complete*
# nonsense, there's never a good reason to do this and so instances of this are almost
# certainly a result of user confusion or error and we want to reject them immediately.
def test_combining_results_of_different_filter_operations_throws_an_error():
    events = SelectTable("events", EVENTS_SCHEMA)
    foo_events = Filter(events, Function.EQ(SelectColumn(events, "code"), Value("foo")))
    bar_events = Filter(events, Function.EQ(SelectColumn(events, "code"), Value("bar")))
    with pytest.raises(DomainMismatchError):
        Function.EQ(SelectColumn(foo_events, "date"), SelectColumn(bar_events, "date"))


# And once a table has been filtered, we can no longer combine the results with the filtered table
def test_combining_filtered_results_with_the_original_table_throws_an_error():
    events = SelectTable("events", EVENTS_SCHEMA)
    foo_events = Filter(events, Function.EQ(SelectColumn(events, "code"), Value("foo")))
    with pytest.raises(DomainMismatchError):
        Function.EQ(SelectColumn(foo_events, "date"), SelectColumn(events, "date"))


# And in particular we can't filter a frame using a predicate derived from a different
# filter operation. Again, this isn't complete nonsense but it's not the best way to
# express the query and is most probably the result of confusion.
def test_filtering_frame_using_result_derived_from_another_filter_throws_error():
    events = SelectTable("events", EVENTS_SCHEMA)
    older_events = Filter(
        events,
        Function.LT(SelectColumn(events, "date"), Value(datetime.date(2022, 1, 1))),
    )
    recent_events = Filter(
        events,
        Function.GE(SelectColumn(events, "date"), Value(datetime.date(2022, 1, 1))),
    )
    is_recent_foo_event = Function.EQ(SelectColumn(recent_events, "code"), Value("foo"))
    with pytest.raises(DomainMismatchError):
        Filter(older_events, is_recent_foo_event)


# However, it's fine to filter a Frame using a predicate derived from a direct ancenstor
# of that Frame. This is important because it allows us to provide a "fluent" interface to
# the Query Model. Without this, every time you wanted to filter a Frame you'd need a
# reference to that Frame to use in the filter condition. And that would make it
# impossible to use chained constructions like:
#
#     events.filter(...).filter(events.date > ...)
#
def test_filtering_frame_using_condition_derived_from_parent_frame_is_ok():
    events = SelectTable("events", EVENTS_SCHEMA)
    foo_events = Filter(events, Function.EQ(SelectColumn(events, "code"), Value("foo")))
    recent_foo_events = Filter(
        foo_events,
        # Note that we're filtering `foo_events` using a condition derived from `events`
        Function.GE(SelectColumn(events, "date"), Value(datetime.date(2022, 1, 1))),
    )
    assert recent_foo_events


# But not the other way around...
def test_filtering_frame_using_condition_derived_from_child_frame_is_not_ok():
    events = SelectTable("events", EVENTS_SCHEMA)
    foo_events = Filter(events, Function.EQ(SelectColumn(events, "code"), Value("foo")))
    with pytest.raises(DomainMismatchError):
        Filter(
            events,
            # Here we're filtering `events` using a condition derived from `foo_events`
            Function.GE(
                SelectColumn(foo_events, "date"), Value(datetime.date(2022, 1, 1))
            ),
        )


# And similarly for sort, we can't sort on a series derived from a divergent filter
def test_sorting_frame_using_result_derived_from_another_filter_throws_error():
    events = SelectTable("events", EVENTS_SCHEMA)
    older_events = Filter(
        events,
        Function.LT(SelectColumn(events, "date"), Value(datetime.date(2022, 1, 1))),
    )
    recent_events = Filter(
        events,
        Function.GE(SelectColumn(events, "date"), Value(datetime.date(2022, 1, 1))),
    )
    recent_codes = SelectColumn(recent_events, "code")
    with pytest.raises(DomainMismatchError):
        Sort(older_events, recent_codes)


# But we can sort using a series derived from an ancestor, to allow this kind of construction:
#
#     events.filter(...).sort(events.date)
#
def test_sorting_frame_using_condition_derived_from_parent_frame_is_ok():
    events = SelectTable("events", EVENTS_SCHEMA)
    foo_events = Filter(events, Function.EQ(SelectColumn(events, "code"), Value("foo")))
    sorted_foo_events = Sort(foo_events, SelectColumn(events, "date"))
    assert sorted_foo_events


# But not the other way around...
def test_sorting_frame_using_value_derived_from_child_frame_is_not_ok():
    events = SelectTable("events", EVENTS_SCHEMA)
    foo_events = Filter(events, Function.EQ(SelectColumn(events, "code"), Value("foo")))
    with pytest.raises(DomainMismatchError):
        Sort(events, SelectColumn(foo_events, "date"))


def test_can_aggregate_a_many_rows_per_patient_series():
    events = SelectTable("events", EVENTS_SCHEMA)
    dates = SelectColumn(events, "date")
    assert AggregateByPatient.Max(dates)


def test_cannot_aggregate_a_one_row_per_patient_series():
    events = SelectTable("events", EVENTS_SCHEMA)
    dates = SelectColumn(events, "date")
    first_event = PickOneRowPerPatient(Sort(events, dates), Position.FIRST)
    first_date = SelectColumn(first_event, "date")
    with pytest.raises(DomainMismatchError):
        AggregateByPatient.Max(first_date)


def test_domain_get_node():
    events = SelectTable("events", EVENTS_SCHEMA)
    # This filter operation creates a new domain
    older_events = Filter(
        events,
        Function.LT(SelectColumn(events, "date"), Value(datetime.date(2022, 1, 1))),
    )
    # But the Sort and SelectColumn doesn't
    sorted_by_date = Sort(older_events, SelectColumn(events, "date"))
    codes_by_date = SelectColumn(sorted_by_date, "code")
    domain = get_domain(codes_by_date)
    # So the node corresponding to the domain should be the Filter
    assert domain.get_node() == older_events


def test_domain_get_node_fails_for_patient_domain():
    patient_domain = get_domain(Value("abc"))
    with pytest.raises(AssertionError):
        patient_domain.get_node()


# TEST TYPE VALIDATION
#


def test_cannot_pick_row_from_unsorted_table():
    events = SelectTable("events", EVENTS_SCHEMA)
    with pytest.raises(TypeValidationError):
        PickOneRowPerPatient(events, Position.FIRST)  # type: ignore


def test_cannot_sort_by_non_comparable_type():
    events = SelectTable("events", EVENTS_SCHEMA)
    bool_column = SelectColumn(events, "flag")
    with pytest.raises(TypeValidationError):
        Sort(events, bool_column)


def test_cannot_pass_argument_without_wrapping_in_value():
    events = SelectTable("events", EVENTS_SCHEMA)
    date = SelectColumn(events, "date")
    with pytest.raises(TypeValidationError):
        Function.EQ(date, datetime.date(2020, 1, 1))  # type: ignore


def test_cannot_compare_date_and_int():
    events = SelectTable("events", EVENTS_SCHEMA)
    date = SelectColumn(events, "date")
    with pytest.raises(TypeValidationError):
        Function.EQ(date, Value(2000))


def test_cannot_define_operation_returning_any_type(queries):
    # This is a guard against future programmer error. It's legitimate to have
    # operations which accept Any, but it's never valid as a return type and it should
    # trigger an assertion if we ever try to define and use such an operation.
    class BadOperation(Series[Any]):
        source: Series[Any]

    with pytest.raises(AssertionError, match=r"never return Series\[Any\]"):
        get_series_type(BadOperation(queries.vaccination_count))


def test_any_type_acts_as_an_escape_hatch():
    # In the `query_model_transforms` module we define new node types which are purely
    # for internal use by the query engines and don't form part of the public query
    # model API. We sometimes want to use types here without having to add support for
    # them in the type checking system, which is already "cleverer" than anyone would
    # like. This test ensures that `Any` can be used as an escape hatch.

    mixed_set = {1, 2.0, "three"}

    # Confirm that we can't validate heterogeneous sets
    class SomePublicOperation(Series):
        value: set[Any]

    with pytest.raises(TypeError, match=r"Sets must be of homogeneous type"):
        SomePublicOperation(value=mixed_set)

    # Confirm that we can nevertheless use such a value as long as we don't care what
    # type it is
    class SomeInternalOperation(Series):
        value: Any

    assert SomeInternalOperation(value=mixed_set)


def test_comparions_between_value_nodes_are_strict():
    assert Value(10) == Value(10)
    assert Value(10) != Value(10.0)
    assert Value(1) != Value(True)
