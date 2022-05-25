import datetime

import sqlalchemy

from databuilder.codes import SNOMEDCTCode
from databuilder.query_language import build_event_table, build_patient_table

from ..lib.util import next_id, null

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
    },
)


Base = sqlalchemy.orm.declarative_base()


class PatientLevelTable(Base):
    __tablename__ = "patient_level_table"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, default=next_id)
    patient_id = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    i1 = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    i2 = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    b1 = sqlalchemy.Column(sqlalchemy.Boolean, default=null)
    b2 = sqlalchemy.Column(sqlalchemy.Boolean, default=null)
    c1 = sqlalchemy.Column(sqlalchemy.Text, default=null)
    d1 = sqlalchemy.Column(sqlalchemy.Date, default=null)
    d2 = sqlalchemy.Column(sqlalchemy.Date, default=null)


class EventLevelTable(Base):
    __tablename__ = "event_level_table"
    Id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, default=next_id)
    patient_id = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    i1 = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    i2 = sqlalchemy.Column(sqlalchemy.Integer, default=null)
    b1 = sqlalchemy.Column(sqlalchemy.Boolean, default=null)
    b2 = sqlalchemy.Column(sqlalchemy.Boolean, default=null)
    c1 = sqlalchemy.Column(sqlalchemy.Text, default=null)
    d1 = sqlalchemy.Column(sqlalchemy.Date, default=null)
    d2 = sqlalchemy.Column(sqlalchemy.Date, default=null)
