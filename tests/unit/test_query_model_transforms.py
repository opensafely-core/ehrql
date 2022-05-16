from databuilder.query_model import (
    PickOneRowPerPatient,
    Position,
    SelectColumn,
    SelectTable,
    Sort,
)
from databuilder.query_model_transforms import (
    PickOneRowPerPatientWithColumns,
    apply_transforms,
)


def test_pick_one_row_per_patient_transform():
    events = SelectTable("events")
    date = SelectColumn(events, "date")
    by_date = Sort(events, date)
    first_event = PickOneRowPerPatient(by_date, Position.FIRST)
    variables = dict(
        first_code=SelectColumn(first_event, "code"),
        first_value=SelectColumn(first_event, "value"),
    )

    first_event_with_columns = PickOneRowPerPatientWithColumns(
        source=by_date,
        position=Position.FIRST,
        selected_columns=frozenset(
            {
                SelectColumn(
                    source=by_date,
                    name="value",
                ),
                SelectColumn(
                    source=by_date,
                    name="code",
                ),
            }
        ),
    )
    expected = {
        "first_code": SelectColumn(first_event_with_columns, "code"),
        "first_value": SelectColumn(first_event_with_columns, "value"),
    }

    transformed = apply_transforms(variables)
    assert transformed == expected
