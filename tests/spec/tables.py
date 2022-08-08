import datetime

import sqlalchemy.orm

from databuilder.codes import SNOMEDCTCode
from databuilder.query_language import EventFrame, PatientFrame, Series, construct

from ..lib.util import orm_class_from_table


@construct
class patient_level_table(PatientFrame):
    i1 = Series(int)
    i2 = Series(int)
    b1 = Series(bool)
    b2 = Series(bool)
    c1 = Series(SNOMEDCTCode)
    d1 = Series(datetime.date)
    d2 = Series(datetime.date)
    s1 = Series(str)
    s2 = Series(str)


@construct
class event_level_table(EventFrame):
    i1 = Series(int)
    i2 = Series(int)
    b1 = Series(bool)
    b2 = Series(bool)
    c1 = Series(SNOMEDCTCode)
    d1 = Series(datetime.date)
    d2 = Series(datetime.date)
    s1 = Series(str)
    s2 = Series(str)


# Define short aliases for terser tests
p = patient_level_table
e = event_level_table

Base = sqlalchemy.orm.declarative_base()
PatientLevelTable = orm_class_from_table(Base, patient_level_table)
EventLevelTable = orm_class_from_table(Base, event_level_table)
