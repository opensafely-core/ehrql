import datetime

import sqlalchemy.orm

from databuilder.codes import SNOMEDCTCode
from databuilder.orm_factory import orm_class_from_ql_table
from databuilder.tables import EventFrame, PatientFrame, Series, table


@table
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
    f1 = Series(float)
    f2 = Series(float)


@table
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
    f1 = Series(float)
    f2 = Series(float)


# Define short aliases for terser tests
p = patient_level_table
e = event_level_table

Base = sqlalchemy.orm.declarative_base()
PatientLevelTable = orm_class_from_ql_table(Base, patient_level_table)
EventLevelTable = orm_class_from_ql_table(Base, event_level_table)
