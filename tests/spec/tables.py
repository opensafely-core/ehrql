import datetime

import sqlalchemy.orm

from databuilder.codes import SNOMEDCTCode
from databuilder.query_language import build_event_table, build_patient_table

from ..lib.util import orm_class_from_table

p = build_patient_table(
    "patient_level_table",
    {
        "i1": int,
        "i2": int,
        "b1": bool,
        "b2": bool,
        "c1": SNOMEDCTCode,
        "d1": datetime.date,
        "d2": datetime.date,
        "s1": str,
        "s2": str,
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
        "d1": datetime.date,
        "d2": datetime.date,
        "s1": str,
        "s2": str,
    },
)


Base = sqlalchemy.orm.declarative_base()
PatientLevelTable = orm_class_from_table(Base, p)
EventLevelTable = orm_class_from_table(Base, e)
