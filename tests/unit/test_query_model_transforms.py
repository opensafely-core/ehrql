import datetime

from databuilder.query_model import (
    Column,
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Sort,
    TableSchema,
)
from databuilder.query_model_transforms import (
    PickOneRowPerPatientWithColumns,
    apply_transforms,
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
    variables = dict(
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
                    source=events,
                    name="value",
                ),
                SelectColumn(
                    source=events,
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

    transformed = apply_transforms(variables)
    assert transformed == expected


def test_adds_one_selected_column_to_sorts():
    events = SelectTable(
        "events",
        TableSchema(i1=Column(int), i2=Column(int)),
    )
    by_i1 = Sort(events, SelectColumn(events, "i1"))
    variables = dict(
        v=SelectColumn(
            PickOneRowPerPatient(source=by_i1, position=Position.FIRST), "i2"
        ),
    )

    transformed = apply_transforms(variables)

    by_i2 = Sort(events, SelectColumn(events, "i2"))
    by_i2_then_i1 = Sort(by_i2, SelectColumn(events, "i1"))
    expected_variables = dict(
        v=SelectColumn(
            PickOneRowPerPatientWithColumns(
                by_i2_then_i1,
                Position.FIRST,
                selected_columns=frozenset(
                    {
                        SelectColumn(
                            source=events,
                            name="i2",
                        ),
                    }
                ),
            ),
            "i2",
        ),
    )

    assert transformed == expected_variables


def test_adds_sorts_at_lowest_priority():
    events = SelectTable(
        "events",
        TableSchema(i1=Column(int), i2=Column(int), i3=Column(int)),
    )
    by_i2 = Sort(events, SelectColumn(events, "i2"))
    by_i2_then_i1 = Sort(by_i2, SelectColumn(events, "i1"))
    variables = dict(
        v=SelectColumn(
            PickOneRowPerPatient(source=by_i2_then_i1, position=Position.FIRST), "i3"
        ),
    )

    transformed = apply_transforms(variables)

    by_i3 = Sort(events, SelectColumn(events, "i3"))
    by_i3_then_i2 = Sort(by_i3, SelectColumn(events, "i2"))
    by_i3_then_i2_then_i1 = Sort(by_i3_then_i2, SelectColumn(events, "i1"))
    expected_variables = dict(
        v=SelectColumn(
            PickOneRowPerPatientWithColumns(
                by_i3_then_i2_then_i1,
                Position.FIRST,
                selected_columns=frozenset(
                    {
                        SelectColumn(
                            source=events,
                            name="i3",
                        ),
                    }
                ),
            ),
            "i3",
        ),
    )

    assert transformed == expected_variables


def test_doesnt_duplicate_existing_sorts():
    events = SelectTable(
        "events",
        TableSchema(i1=Column(int)),
    )
    by_i1 = Sort(events, SelectColumn(events, "i1"))
    variables = dict(
        v=SelectColumn(
            PickOneRowPerPatient(source=by_i1, position=Position.FIRST), "i1"
        ),
    )

    transformed = apply_transforms(variables)

    expected_variables = dict(
        v=SelectColumn(
            PickOneRowPerPatientWithColumns(
                by_i1,
                Position.FIRST,
                selected_columns=frozenset(
                    {
                        SelectColumn(
                            source=events,
                            name="i1",
                        ),
                    }
                ),
            ),
            "i1",
        ),
    )

    assert transformed == expected_variables


def test_adds_sorts_in_lexical_order_of_column_names():
    events = SelectTable(
        "events",
        TableSchema(i1=Column(int), iz=Column(int), ia=Column(int)),
    )
    by_i1 = Sort(events, SelectColumn(events, "i1"))
    first_initial = PickOneRowPerPatient(source=by_i1, position=Position.FIRST)
    variables = dict(
        z=SelectColumn(first_initial, "iz"),
        a=SelectColumn(first_initial, "ia"),
    )

    transformed = apply_transforms(variables)

    by_iz = Sort(events, SelectColumn(events, "iz"))
    by_iz_then_ia = Sort(by_iz, SelectColumn(events, "ia"))
    by_iz_then_ia_then_i1 = Sort(by_iz_then_ia, SelectColumn(events, "i1"))
    first_with_extra_sorts = PickOneRowPerPatientWithColumns(
        by_iz_then_ia_then_i1,
        Position.FIRST,
        selected_columns=frozenset(
            {
                SelectColumn(
                    source=events,
                    name="iz",
                ),
                SelectColumn(
                    source=events,
                    name="ia",
                ),
            }
        ),
    )
    expected_variables = dict(
        z=SelectColumn(first_with_extra_sorts, "iz"),
        a=SelectColumn(first_with_extra_sorts, "ia"),
    )

    assert transformed == expected_variables
