from databuilder.contracts import types
from databuilder.contracts.base import Column, TableContract
from databuilder.contracts.constraints import (
    FirstOfMonthConstraint,
    NotNullConstraint,
    UniqueConstraint,
)


class Patients(TableContract):
    _name = "patients"

    patient_id = Column(
        type=types.PseudoPatientId(),
        constraints=[NotNullConstraint(), UniqueConstraint()],
    )
    height = Column(
        type=types.Integer(),
    )
    date_of_birth = Column(
        type=types.Date(),
        constraints=[NotNullConstraint(), FirstOfMonthConstraint()],
    )
    sex = Column(
        type=types.Choice("female", "male", "intersex", "unknown"),
        constraints=[NotNullConstraint()],
    )


class Registrations(TableContract):
    _name = "practice_registrations"

    patient_id = Column(
        type=types.PseudoPatientId(),
    )
    stp = Column(
        type=types.String(),
    )
    date_start = Column(
        type=types.Date(),
    )
    date_end = Column(
        type=types.Date(),
    )


class Events(TableContract):
    _name = "clinical_events"

    patient_id = Column(
        type=types.PseudoPatientId(),
    )
    code = Column(
        type=types.Code(),
    )
    date = Column(
        type=types.Date(),
    )
    value = Column(
        type=types.Integer(),
    )


class Tests(TableContract):
    _name = "positive_tests"

    patient_id = Column(
        type=types.PseudoPatientId(),
    )
    result = Column(
        type=types.Boolean(),
    )
    test_date = Column(
        type=types.Date(),
    )


class P(TableContract):
    _name = "p"
    patient_id = Column(type=types.PseudoPatientId())
    i1 = Column(type=types.Integer())
    i2 = Column(type=types.Integer())
    b1 = Column(type=types.Boolean())
    b2 = Column(type=types.Boolean())


class E(TableContract):
    _name = "e"
    patient_id = Column(type=types.PseudoPatientId())
    i1 = Column(type=types.Integer())
    i2 = Column(type=types.Integer())
    b1 = Column(type=types.Boolean())
    b2 = Column(type=types.Boolean())
