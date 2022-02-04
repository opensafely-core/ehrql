import pytest

from databuilder.query_model import (
    AggregateByPatient,
    Code,
    DomainMismatchError,
    Filter,
    Function,
    OneRowPerPatientFrame,
    OneRowPerPatientSeries,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Sort,
)


def test_construct_basic_query():
    events = SelectTable("events")
    code = SelectColumn(events, "code")
    date = SelectColumn(events, "date")
    vaccinations = Filter(events, Function.EQ(code, Code("abc123", system="ctv3")))
    has_vaccination = AggregateByPatient.Exists(vaccinations)
    first_vaccination = PickOneRowPerPatient(Sort(vaccinations, date), Position.FIRST)
    assert isinstance(has_vaccination, OneRowPerPatientSeries)
    assert isinstance(first_vaccination, OneRowPerPatientFrame)


def test_mixing_domains_throws_error():
    events = SelectTable("events")
    vaccinations = SelectTable("vaccinations")
    vaccine_code = SelectColumn(vaccinations, "code")
    with pytest.raises(DomainMismatchError):
        Filter(events, Function.EQ(vaccine_code, Code("abc123", system="ctv3")))
