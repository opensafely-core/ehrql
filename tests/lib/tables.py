from databuilder.dsl import (
    BoolColumn,
    CodeColumn,
    DateColumn,
    EventTable,
    IdColumn,
    IntColumn,
    PatientTable,
    StrColumn,
)

from . import contracts


class Patients(PatientTable):
    patient_id = IdColumn("patient_id")
    height = IntColumn("height")
    date_of_birth = DateColumn("date_of_birth")
    sex = StrColumn("sex")


patients = Patients(contracts.Patients)


class Registrations(EventTable):
    patient_id = IdColumn("patient_id")
    stp = StrColumn("stp")
    date_start = DateColumn("date_start")
    date_end = DateColumn("date_end")


registrations = Registrations(contracts.Registrations)


class Events(EventTable):
    patient_id = IdColumn("patient_id")
    code = CodeColumn("code")
    date = DateColumn("date")
    value = IntColumn("value")


events = Events(contracts.Events)


class Tests(EventTable):
    patient_id = IdColumn("patient_id")
    result = BoolColumn("result")
    test_date = DateColumn("test_date")


positive_tests = Tests(contracts.Tests)
