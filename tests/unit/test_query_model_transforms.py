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
