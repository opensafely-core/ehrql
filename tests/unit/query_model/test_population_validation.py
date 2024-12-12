import pytest

from ehrql.query_model.nodes import (
    AggregateByPatient,
    Case,
    Column,
    Function,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
    TableSchema,
    Value,
)
from ehrql.query_model.population_validation import (
    EmptyQueryEngine,
    ValidationError,
    validate_population_definition,
)


def test_rejects_non_series():
    aint_no_series = "I am not a Series"
    with pytest.raises(ValidationError, match="must be a `query_model.Series`"):
        validate_population_definition(aint_no_series)


def test_rejects_invalid_dimension():
    event_series = SelectColumn(
        SelectTable("events", schema=TableSchema(value=Column(bool))), "value"
    )
    with pytest.raises(ValidationError, match="one-row-per-patient series"):
        validate_population_definition(event_series)


def test_rejects_invalid_type():
    int_series = SelectColumn(
        SelectPatientTable("patients", schema=TableSchema(value=Column(int))), "value"
    )
    with pytest.raises(ValidationError, match="boolean type"):
        validate_population_definition(int_series)


def test_accepts_basic_reasonable_population():
    has_registration = AggregateByPatient.Exists(
        SelectTable("registrations", schema=TableSchema(value=Column(int)))
    )
    assert validate_population_definition(has_registration)


def test_rejects_basic_unreasonable_population():
    not_died = Function.Not(
        AggregateByPatient.Exists(
            SelectTable("ons_deaths", schema=TableSchema(value=Column(int)))
        )
    )
    with pytest.raises(ValidationError, match="must not evaluate as True for NULL"):
        validate_population_definition(not_died)


# TEST SERIES EVALUATION AGAINST EMPTY DATABASE
#

patients = SelectPatientTable("patients", schema=TableSchema(value=Column(int)))
events = SelectTable("events", schema=TableSchema(value=Column(int)))
patients_value = SelectColumn(patients, "value")
events_value = SelectColumn(events, "value")

cases = [
    (
        True,
        # events.count_for_patient() + 3 >= 3
        Function.GE(
            Function.Add(AggregateByPatient.Count(events), Value(3)),
            Value(3),
        ),
    ),
    (
        False,
        # events.count_for_patient() + 3 >= 4
        Function.GE(
            Function.Add(AggregateByPatient.Count(events), Value(3)),
            Value(4),
        ),
    ),
    (
        True,
        # patients.v.is_null()
        Function.IsNull(patients_value),
    ),
    (
        False,
        # ~patients.v.is_null()
        Function.Not(Function.IsNull(patients_value)),
    ),
    (
        True,
        # events.v.max_for_patient().is_null()
        Function.IsNull(AggregateByPatient.Max(events_value)),
    ),
    (
        False,
        # events.v.max_for_patient() > 100
        Function.GT(
            AggregateByPatient.Max(events_value),
            Value(100),
        ),
    ),
    (
        True,
        # patients.v == 1 | (10 < 20)
        Function.Or(
            Function.EQ(patients_value, Value(1)),
            Function.LT(Value(2), Value(3)),
        ),
    ),
    (
        False,
        # patients.v == 100 | (patients.v <= 20)
        Function.Or(
            Function.EQ(patients_value, Value(100)),
            Function.LE(patients_value, Value(3)),
        ),
    ),
    (
        False,
        # ~patients.v.is_null | events.exists_for_patient()
        Function.Or(
            Function.Not(Function.IsNull(patients_value)),
            AggregateByPatient.Exists(events),
        ),
    ),
    (
        True,
        # (1 == 1) & (2 == 2)
        Function.And(
            Function.EQ(Value(1), Value(1)),
            Function.EQ(Value(2), Value(2)),
        ),
    ),
    (
        False,
        # ~(patients.v == 100 & events.exists_for_patient())
        Function.And(
            Function.EQ(patients_value, Value(100)),
            AggregateByPatient.Exists(events),
        ),
    ),
    (
        False,
        # patients.v == 1 & events.v.sum_for_patient() == 2
        Function.And(
            Function.EQ(patients_value, Value(1)),
            Function.EQ(AggregateByPatient.Sum(events_value), Value(2)),
        ),
    ),
    (
        True,
        Function.In(Value(10), Value(frozenset([30, 20, 10]))),
    ),
    (
        True,
        Case(
            {
                Function.EQ(patients_value, Value(1)): Value(False),
                Function.EQ(Value(1), Value(1)): Value(True),
            },
            default=None,
        ),
    ),
    (
        True,
        Case(
            {
                Function.EQ(patients_value, Value(1)): Value(False),
                Function.EQ(patients_value, Value(2)): Value(False),
            },
            default=Value(True),
        ),
    ),
    (
        True,
        Function.StringContains(Value("foobar"), Value("oba")),
    ),
    (
        False,
        Function.StringContains(Value("foo bar"), Value("oba")),
    ),
]


@pytest.mark.parametrize("expected,query", cases)
def test_series_evaluates_true(expected, query):
    result = EmptyQueryEngine(None).series_evaluates_true(query)
    assert result == expected, f"Expected {expected}, got {result} in:\n{query}"
