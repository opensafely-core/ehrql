import datetime
from types import SimpleNamespace

import pytest

from databuilder.query_model import (
    AggregateByPatient,
    Categorise,
    DomainMismatchError,
    Filter,
    Frame,
    Function,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Series,
    Sort,
    TableSchema,
    Value,
)

EVENTS_SCHEMA = TableSchema(
    "EVENTS_SCHEMA", patient_id=int, date=datetime.date, code=str
)


@pytest.fixture
def queries():
    q = SimpleNamespace()
    events = SelectTable("events", EVENTS_SCHEMA)
    code = SelectColumn(events, "code")
    date = SelectColumn(events, "date")
    vaccinations = Filter(events, Function.EQ(code, Value("abc123")))
    anaphylaxis_events = Filter(
        events, Function.In(code, Value(frozenset({"def456", "xyz789"})))
    )

    q.vaccination_count = AggregateByPatient.Count(
        SelectColumn(vaccinations, "patient_id")
    )
    q.first_vaccination = PickOneRowPerPatient(Sort(vaccinations, date), Position.FIRST)
    q.vaccination_status = Categorise(
        {
            Value("partial"): Function.EQ(q.vaccination_count, Value(1)),
            Value("full"): Function.EQ(q.vaccination_count, Value(2)),
            Value("boosted"): Function.GE(q.vaccination_count, Value(3)),
        },
        default=Value("unvaccinated"),
    )

    q.vaccination_days = SelectColumn(vaccinations, "date")
    q.vaccination_days_set = AggregateByPatient.CombineAsSet(q.vaccination_days)
    q.anaphylaxis_co_occurance = Filter(
        anaphylaxis_events, Function.In(date, q.vaccination_days_set)
    )
    q.had_anaphylaxis = AggregateByPatient.Exists(
        SelectColumn(q.anaphylaxis_co_occurance, "patient_id")
    )

    return q


def test_queries_have_expected_types(queries):
    assert isinstance(queries.vaccination_count, Series)
    assert isinstance(queries.first_vaccination, Frame)
    assert isinstance(queries.vaccination_status, Series)
    assert isinstance(queries.vaccination_days, Series)
    assert isinstance(queries.vaccination_days_set, Series)
    assert isinstance(queries.anaphylaxis_co_occurance, Frame)
    assert isinstance(queries.had_anaphylaxis, Series)


def test_queries_are_hashable(queries):
    for query in vars(queries).values():
        assert hash(query) is not None


# We don't _have_ to maintain this property, but it's quite a convenient one to have and
# if we're going to break it then let's at least do so deliberately
def test_query_reprs_round_trip(queries):
    # This relies on all public query model names being imported into local scope
    for query in vars(queries).values():
        assert eval(repr(query)) == query


def test_mixing_domains_throws_error():
    events = SelectTable("events")
    vaccinations = SelectTable("vaccinations")
    vaccine_code = SelectColumn(vaccinations, "code")
    with pytest.raises(DomainMismatchError):
        Filter(events, Function.EQ(vaccine_code, Value("abc123")))
