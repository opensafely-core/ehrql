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


@pytest.mark.parametrize(
    ("year", "start", "end"),
    [
        (1, datetime.date(1, 1, 1), datetime.date(2, 1, 1)),
        (2020, datetime.date(2020, 1, 1), datetime.date(2021, 1, 1)),
        (2021, datetime.date(2021, 1, 1), datetime.date(2022, 1, 1)),
        (9998, datetime.date(9998, 1, 1), datetime.date(9999, 1, 1)),
    ],
)
def test_year_equality_rewrites_to_bounded_date_range(year, start, end):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")

    transformed = apply_transforms(
        Function.EQ(Function.YearFromDate(event_date), Value(year))
    )

    assert transformed == Function.And(
        Function.GE(event_date, Value(start)),
        Function.LT(event_date, Value(end)),
    )


@pytest.mark.parametrize(
    ("comparison", "comparison_date", "expected_operator", "bound_date"),
    [
        ("LT", datetime.date(2020, 3, 1), "LT", datetime.date(2020, 3, 1)),
        ("LT", datetime.date(2020, 3, 15), "LT", datetime.date(2020, 4, 1)),
        ("LE", datetime.date(2020, 3, 1), "LT", datetime.date(2020, 4, 1)),
        ("GT", datetime.date(2020, 3, 31), "GE", datetime.date(2020, 4, 1)),
        ("LE", datetime.date(2020, 12, 15), "LT", datetime.date(2021, 1, 1)),
        ("GE", datetime.date(2020, 3, 1), "GE", datetime.date(2020, 3, 1)),
        ("GE", datetime.date(2020, 3, 15), "GE", datetime.date(2020, 4, 1)),
    ],
)
def test_to_first_of_month_ordered_comparison_rewrites_to_date_bound(
    comparison, comparison_date, expected_operator, bound_date
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Function.ToFirstOfMonth(event_date), Value(comparison_date)
    )

    assert apply_transforms(expression) == getattr(Function, expected_operator)(
        event_date, Value(bound_date)
    )


@pytest.mark.parametrize(
    ("comparison_date", "should_rewrite"),
    [
        (datetime.date(2020, 3, 1), True),
        (datetime.date(2020, 3, 15), False),
    ],
)
def test_to_first_of_month_equality_only_rewritten_for_first_of_month(
    comparison_date, should_rewrite
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = Function.EQ(
        Function.ToFirstOfMonth(event_date), Value(comparison_date)
    )

    if should_rewrite:
        expected_expression = Function.And(
            Function.GE(event_date, Value(datetime.date(2020, 3, 1))),
            Function.LT(event_date, Value(datetime.date(2020, 4, 1))),
        )
    else:
        expected_expression = expression
    assert apply_transforms(expression) == expected_expression


@pytest.mark.parametrize(
    ("comparison", "expected_operator", "expected_date"),
    [
        ("EQ", None, None),
        ("LT", "GE", datetime.date(2020, 4, 1)),
        ("LE", "GE", datetime.date(2020, 4, 1)),
        ("GT", "LT", datetime.date(2020, 4, 1)),
        ("GE", "LT", datetime.date(2020, 4, 1)),
    ],
)
def test_to_first_of_month_comparison_handles_reversed_operands(
    comparison, expected_operator, expected_date
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    comparison_date = datetime.date(2020, 3, 15)
    expression = getattr(Function, comparison)(
        Value(comparison_date), Function.ToFirstOfMonth(event_date)
    )

    if expected_operator is None:
        expected_expression = expression
    else:
        expected_expression = getattr(Function, expected_operator)(
            event_date, Value(expected_date)
        )
    assert apply_transforms(expression) == expected_expression


@pytest.mark.parametrize(
    ("comparison", "comparison_date"),
    [
        ("EQ", datetime.date(9999, 12, 1)),
        ("LT", datetime.date(9999, 12, 2)),
        ("LE", datetime.date(9999, 12, 31)),
        ("GT", datetime.date(9999, 12, 1)),
        ("GE", datetime.date(9999, 12, 2)),
    ],
)
def test_to_first_of_month_comparison_needing_unrepresentable_next_month_is_unchanged(
    comparison, comparison_date
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Function.ToFirstOfMonth(event_date), Value(comparison_date)
    )

    assert apply_transforms(expression) == expression


@pytest.mark.parametrize(
    ("comparison", "comparison_date"),
    [
        ("LT", datetime.date(9999, 12, 1)),
        ("GE", datetime.date(9999, 12, 1)),
    ],
)
def test_to_first_of_month_comparison_at_year_limit_uses_date_literal(
    comparison, comparison_date
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Function.ToFirstOfMonth(event_date), Value(comparison_date)
    )

    assert apply_transforms(expression) == getattr(Function, comparison)(
        event_date, Value(comparison_date)
    )


@pytest.mark.parametrize(
    ("comparison", "comparison_date", "expected_operator", "bound_year"),
    [
        ("LT", datetime.date(2020, 1, 1), "LT", 2020),
        ("LT", datetime.date(2020, 4, 1), "LT", 2021),
        ("LE", datetime.date(2020, 1, 1), "LT", 2021),
        ("GT", datetime.date(2020, 12, 31), "GE", 2021),
        ("GE", datetime.date(2020, 1, 1), "GE", 2020),
        ("GE", datetime.date(2020, 4, 1), "GE", 2021),
    ],
)
def test_to_first_of_year_ordered_comparison_rewrites_to_date_bound(
    comparison, comparison_date, expected_operator, bound_year
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Function.ToFirstOfYear(event_date), Value(comparison_date)
    )

    assert apply_transforms(expression) == getattr(Function, expected_operator)(
        event_date, Value(datetime.date(bound_year, 1, 1))
    )


@pytest.mark.parametrize(
    ("comparison_date", "should_rewrite"),
    [
        (datetime.date(2020, 1, 1), True),
        (datetime.date(2020, 1, 2), False),
        (datetime.date(2020, 2, 29), False),
    ],
)
def test_to_first_of_year_equality_only_rewritten_for_jan_1(
    comparison_date, should_rewrite
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = Function.EQ(Function.ToFirstOfYear(event_date), Value(comparison_date))

    if should_rewrite:
        expected_expression = Function.And(
            Function.GE(event_date, Value(datetime.date(2020, 1, 1))),
            Function.LT(event_date, Value(datetime.date(2021, 1, 1))),
        )
    else:
        expected_expression = expression
    assert apply_transforms(expression) == expected_expression


@pytest.mark.parametrize(
    ("comparison", "expected_operator", "expected_year"),
    [
        ("EQ", None, None),
        ("LT", "GE", 2021),
        ("LE", "GE", 2021),
        ("GT", "LT", 2021),
        ("GE", "LT", 2021),
    ],
)
def test_to_first_of_year_comparison_handles_reversed_operands(
    comparison, expected_operator, expected_year
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    comparison_date = datetime.date(2020, 4, 1)
    expression = getattr(Function, comparison)(
        Value(comparison_date), Function.ToFirstOfYear(event_date)
    )

    if expected_operator is None:
        expected_expression = expression
    else:
        expected_expression = getattr(Function, expected_operator)(
            event_date, Value(datetime.date(expected_year, 1, 1))
        )
    assert apply_transforms(expression) == expected_expression


@pytest.mark.parametrize(
    ("comparison", "comparison_date"),
    [
        ("EQ", datetime.date(9999, 1, 1)),
        ("LT", datetime.date(9999, 3, 1)),
        ("LE", datetime.date(9999, 12, 31)),
        ("GT", datetime.date(9999, 1, 1)),
        ("GE", datetime.date(9999, 12, 31)),
    ],
)
def test_to_first_of_year_comparison_in_year_9999_is_unchanged(
    comparison, comparison_date
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Function.ToFirstOfYear(event_date), Value(comparison_date)
    )

    assert apply_transforms(expression) == expression


@pytest.mark.parametrize(
    ("comparison", "year", "bound_year", "expected_comparison"),
    [
        ("LT", 1, 1, "LT"),
        ("LT", 2020, 2020, "LT"),
        ("LE", 2020, 2021, "LT"),
        ("LE", 9998, 9999, "LT"),
        ("GT", 2020, 2021, "GE"),
        ("GT", 9998, 9999, "GE"),
        ("GE", 2020, 2020, "GE"),
    ],
)
def test_ordered_year_comparisons_rewrite_to_date_bound(
    comparison, year, bound_year, expected_comparison
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Function.YearFromDate(event_date),
        Value(year),
    )

    assert apply_transforms(expression) == getattr(Function, expected_comparison)(
        event_date,
        Value(datetime.date(bound_year, 1, 1)),
    )


@pytest.mark.parametrize(
    ("comparison", "expected_comparison", "bound_year"),
    [
        ("LT", "GE", 2021),
        ("LE", "GE", 2020),
        ("GT", "LT", 2020),
        ("GE", "LT", 2021),
    ],
)
def test_ordered_year_comparison_rewrite_handles_reversed_operands(
    comparison, expected_comparison, bound_year
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Value(2020),
        Function.YearFromDate(event_date),
    )

    assert apply_transforms(expression) == getattr(Function, expected_comparison)(
        event_date,
        Value(datetime.date(bound_year, 1, 1)),
    )


@pytest.mark.parametrize(
    ("comparison", "year"),
    [
        ("LT", 9999),
        ("LE", 9999),
        ("GT", 9999),
        ("GE", 9999),
        ("GT", 0),
        ("LT", 0),
        ("GE", 0),
    ],
)
def test_ordered_year_comparisons_outside_transformable_bounds_are_unchanged(
    comparison, year
):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = getattr(Function, comparison)(
        Function.YearFromDate(event_date),
        Value(year),
    )

    assert apply_transforms(expression) == expression


@pytest.mark.parametrize("year", [0, 9999, 10000])
def test_year_equality_outside_transformable_bounds_is_unchanged(year):
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")
    expression = Function.EQ(Function.YearFromDate(event_date), Value(year))

    assert apply_transforms(expression) == expression


def test_year_equality_rewrite_handles_reversed_operands():
    events = SelectTable("dated_events", TableSchema(date=Column(datetime.date)))
    event_date = SelectColumn(events, "date")

    transformed = apply_transforms(
        Function.EQ(Value(2020), Function.YearFromDate(event_date))
    )

    assert transformed == Function.And(
        Function.GE(event_date, Value(datetime.date(2020, 1, 1))),
        Function.LT(event_date, Value(datetime.date(2021, 1, 1))),
    )


def test_year_equality_with_computed_year_is_unchanged():
    events = SelectTable(
        "dated_events",
        TableSchema(date=Column(datetime.date), other_date=Column(datetime.date)),
    )
    event_date = SelectColumn(events, "date")
    other_date = SelectColumn(events, "other_date")
    computed_year = Function.Add(
        Function.YearFromDate(other_date),
        Value(100),
    )
    expression = Function.EQ(Function.YearFromDate(event_date), computed_year)

    assert apply_transforms(expression) == expression


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
