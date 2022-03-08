from databuilder.query_language import (
    BoolSeries,
    IdSeries,
    IntSeries,
    build_event_table,
    build_patient_table,
)

p = build_patient_table(
    "patient_level_table",
    {
        "patient_id": IdSeries,
        "i1": IntSeries,
        "i2": IntSeries,
        "b1": BoolSeries,
        "b2": BoolSeries,
    },
)


e = build_event_table(
    "event_level_table",
    {
        "patient_id": IdSeries,
        "i1": IntSeries,
        "i2": IntSeries,
        "b1": BoolSeries,
        "b2": BoolSeries,
    },
)
