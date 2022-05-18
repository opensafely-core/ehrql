from databuilder.codes import SNOMEDCTCode
from databuilder.query_language import build_event_table, build_patient_table

p = build_patient_table(
    "patient_level_table",
    {
        "i1": int,
        "i2": int,
        "b1": bool,
        "b2": bool,
        "c1": SNOMEDCTCode,
    },
)


e = build_event_table(
    "event_level_table",
    {
        "i1": int,
        "i2": int,
        "b1": bool,
        "b2": bool,
        "c1": SNOMEDCTCode,
    },
)
