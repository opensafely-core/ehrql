import datetime

import pytest

from ehrql.query_model.nodes import (
    Case,
    Column,
    Dataset,
    Function,
    Parameter,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Sort,
    TableSchema,
    Value,
)
from ehrql.query_model.transforms import (
    Coalesce,
    FixedValueMap,
    PickOneRowPerPatientWithColumns,
    apply_transforms,
    rewrite_case_to_coalesce,
    rewrite_case_to_fixed_value_map,
    substitute_parameters,
    unpack_conjunction,
)


def test_pick_one_row_per_patient_transform():
    events = SelectTable(
        "events",
        schema=TableSchema(
            date=Column(datetime.date), code=Column(str), value=Column(float)
        ),
    )
    sorted_events = Sort(
        Sort(
            Sort(
                events,
                SelectColumn(events, "value"),
            ),
            SelectColumn(events, "code"),
        ),
        SelectColumn(events, "date"),
    )
    first_event = PickOneRowPerPatient(sorted_events, Position.FIRST)
    dataset = dataset_factory(
        first_code=SelectColumn(first_event, "code"),
        first_value=SelectColumn(first_event, "value"),
        # Create a new distinct column object with the same value as the first column:
        # equal but not identical objects expose bugs in the query model transformation
        first_code_again=SelectColumn(first_event, "code"),
    )

    first_event_with_columns = PickOneRowPerPatientWithColumns(
        source=sorted_events,
        position=Position.FIRST,
        selected_columns=frozenset(
            {
                SelectColumn(
                    source=sorted_events,
                    name="value",
                ),
                SelectColumn(
                    source=sorted_events,
                    name="code",
                ),
            }
        ),
    )
    expected = {
        "first_code": SelectColumn(first_event_with_columns, "code"),
        "first_value": SelectColumn(first_event_with_columns, "value"),
        "first_code_again": SelectColumn(first_event_with_columns, "code"),
    }

    transformed = apply_transforms(dataset)
    assert transformed.variables == expected


def test_substitute_parameters():
    node = Function.Negate(Function.Add(Value(10), Parameter("i", int)))
    transformed = substitute_parameters(node, i=20)
    assert transformed == Function.Negate(Function.Add(Value(10), Value(20)))


events = SelectTable(
    "events", TableSchema(i1=Column(int), i2=Column(int), s1=Column(str))
)
i1 = SelectColumn(events, "i1")
i2 = SelectColumn(events, "i2")
s1 = SelectColumn(events, "s1")


def test_specialize_case_operations_ignores_unhandled_cases():
    case_dynamic = Case(
        {
            Function.LE(i1, Value(100)): Value("small"),
            Function.GT(i1, Value(100)): Value("large"),
        },
        default=None,
    )

    assert apply_transforms(case_dynamic) == case_dynamic


def test_specialize_case_operations_handles_fixed_value_maps():
    case_fixed = Case(
        {
            Function.EQ(i1, Value(1)): Value("A"),
            Function.EQ(i1, Value(2)): Value("B"),
        },
        default=None,
    )

    assert apply_transforms(case_fixed) == FixedValueMap(
        source=i1,
        mapping={
            Value(1): Value("A"),
            Value(2): Value("B"),
        },
        default=None,
    )


def test_rewrite_case_to_fixed_value_map_backwards_equality():
    case = Case(
        {
            Function.EQ(i1, Value(1)): Value("A"),
            # This expression is the "wrong" way round
            Function.EQ(Value(2), i1): Value("B"),
        },
        default=None,
    )
    fixed_value_map = FixedValueMap(
        source=i1,
        mapping={
            Value(1): Value("A"),
            Value(2): Value("B"),
        },
        default=None,
    )
    assert rewrite_case_to_fixed_value_map(case) == fixed_value_map


def test_rewrite_case_to_fixed_value_map_duplicate_values():
    case = Case(
        {
            Function.EQ(i1, Value(1)): Value("A"),
            Function.EQ(i1, Value(2)): Value("B"),
            # This is equivalent to the first clause and so should never match
            Function.EQ(Value(1), i1): Value("C"),
        },
        default=None,
    )
    fixed_value_map = FixedValueMap(
        source=i1,
        mapping={
            Value(1): Value("A"),
            Value(2): Value("B"),
        },
        default=None,
    )
    assert rewrite_case_to_fixed_value_map(case) == fixed_value_map


def test_rewrite_case_to_fixed_value_map_with_default():
    case = Case(
        {
            Function.EQ(i1, Value(1)): Value("A"),
        },
        default=Value("X"),
    )
    fixed_value_map = FixedValueMap(
        source=i1,
        mapping={
            Value(1): Value("A"),
        },
        default=Value("X"),
    )
    assert rewrite_case_to_fixed_value_map(case) == fixed_value_map


@pytest.mark.parametrize(
    "case",
    [
        # Has clauses which are not simple equality
        Case(
            {
                Function.EQ(i1, Value(1)): Value("A"),
                Function.GT(i1, Value(2)): Value("B"),
            },
            default=None,
        ),
        # Has a "then" value which is not fixed
        Case(
            {
                Function.EQ(i1, Value(1)): s1,
            },
            default=None,
        ),
        # Does not use a consistent source expression
        Case(
            {
                Function.EQ(i1, Value(1)): Value("A"),
                Function.EQ(Function.Negate(i1), Value(-2)): Value("B"),
            },
            default=None,
        ),
        # Uses a dynamic value on the RHS of a clause
        Case(
            {
                Function.EQ(i1, Value(1)): Value("A"),
                Function.EQ(i1, i1): Value("B"),
            },
            default=None,
        ),
        # Uses a dynamic default
        Case(
            {
                Function.EQ(i1, Value(1)): Value("A"),
            },
            default=s1,
        ),
    ],
)
def test_rewrite_case_to_fixed_value_map_rejects(case):
    assert rewrite_case_to_fixed_value_map(case) is None


def test_specialize_case_operations_handles_coalesce():
    case_coalesce = Case(
        {
            Function.Not(Function.IsNull(i1)): i1,
            Function.Not(Function.IsNull(i2)): i2,
        },
        default=Value(0),
    )

    assert apply_transforms(case_coalesce) == Coalesce(
        sources=(i1, i2, Value(0)),
    )


def test_rewrite_case_to_coalesce_without_default():
    case = Case(
        {
            Function.Not(Function.IsNull(i1)): i1,
            Function.Not(Function.IsNull(i2)): i2,
        },
        default=None,
    )
    coalesce = Coalesce(
        sources=(i1, i2),
    )
    assert rewrite_case_to_coalesce(case) == coalesce


def test_rewrite_case_to_coalesce_with_redundant_clause():
    case = Case(
        {
            Function.Not(Function.IsNull(i1)): i1,
            Function.And(
                Function.IsNull(i1),
                Function.Not(Function.IsNull(i2)),
            ): i2,
        },
        default=None,
    )
    coalesce = Coalesce(
        sources=(i1, i2),
    )
    assert rewrite_case_to_coalesce(case) == coalesce


@pytest.mark.parametrize(
    "case",
    [
        # Has a clause which is not a negated null check
        Case(
            {
                Function.Not(Function.IsNull(i1)): i1,
                Function.GT(i2, Value(10)): i2,
            },
            default=None,
        ),
        # Has a null "then" value
        Case(
            {
                Function.Not(Function.IsNull(i1)): i1,
                Function.Not(Function.IsNull(i2)): None,
            },
            default=None,
        ),
        # Has a clause embedded in a conjunction which is not a null check
        Case(
            {
                Function.Not(Function.IsNull(i1)): i1,
                Function.And(
                    Function.Not(Function.IsNull(i2)),
                    Function.GT(i2, Value(10)),
                ): i2,
            },
            default=None,
        ),
    ],
)
def test_rewrite_case_to_coalesce_rejects(case):
    assert rewrite_case_to_coalesce(case) is None


def test_unpack_conjunction():
    bool_1 = Function.EQ(i1, Value(1))
    bool_2 = Function.EQ(i1, Value(2))
    bool_3 = Function.EQ(i1, Value(3))
    bool_4 = Function.EQ(i1, Value(4))
    bool_5 = Function.EQ(i1, Value(5))
    bool_6 = Function.EQ(i1, Value(6))

    nested = Function.And(
        Function.And(
            bool_1,
            Function.Or(bool_2, bool_3),
        ),
        Function.And(
            bool_4,
            Function.And(bool_5, bool_6),
        ),
    )
    assert unpack_conjunction(nested) == {
        bool_1,
        Function.Or(bool_2, bool_3),
        bool_4,
        bool_5,
        bool_6,
    }


def dataset_factory(**variables):
    return Dataset(
        population=Value(False), variables=variables, events={}, measures=None
    )
