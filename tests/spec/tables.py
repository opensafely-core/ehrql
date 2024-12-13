import datetime

from ehrql.codes import ICD10MultiCodeString, OPCS4MultiCodeString, SNOMEDCTCode
from ehrql.tables import EventFrame, PatientFrame, Series, table


@table
class patient_level_table(PatientFrame):
    i1 = Series(int)
    i2 = Series(int)
    b1 = Series(bool)
    b2 = Series(bool)
    c1 = Series(SNOMEDCTCode)
    m1 = Series(ICD10MultiCodeString)
    m2 = Series(OPCS4MultiCodeString)
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
    i3 = Series(int)
    b1 = Series(bool)
    b2 = Series(bool)
    c1 = Series(SNOMEDCTCode)
    m1 = Series(ICD10MultiCodeString)
    m2 = Series(OPCS4MultiCodeString)
    d1 = Series(datetime.date)
    d2 = Series(datetime.date)
    s1 = Series(str)
    s2 = Series(str)
    f1 = Series(float)
    f2 = Series(float)


# Define short aliases for terser tests
p = patient_level_table
e = event_level_table
