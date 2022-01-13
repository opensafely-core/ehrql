from databuilder.dsl import (
    BoolColumn,
    CodeColumn,
    DateColumn,
    EventFrame,
    IdColumn,
    IntColumn,
    PatientFrame,
    StrColumn,
)

from . import contracts


class Patients(PatientFrame):
    patient_id = IdColumn("patient_id")
    height = IntColumn("height")
    date_of_birth = DateColumn("date_of_birth")
    sex = StrColumn("sex")


patients = Patients.from_contract(contracts.Patients)


class Registrations(EventFrame):
    patient_id = IdColumn("patient_id")
    stp = StrColumn("stp")
    date_start = DateColumn("date_start")
    date_end = DateColumn("date_end")


registrations = Registrations.from_contract(contracts.Registrations)


class Events(EventFrame):
    patient_id = IdColumn("patient_id")
    code = CodeColumn("code")
    date = DateColumn("date")
    value = IntColumn("value")


events = Events.from_contract(contracts.Events)


class Tests(EventFrame):
    patient_id = IdColumn("patient_id")
    result = BoolColumn("result")
    test_date = DateColumn("test_date")


positive_tests = Tests.from_contract(contracts.Tests)
