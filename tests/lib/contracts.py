from databuilder.contracts import types
from databuilder.contracts.base import Column, TableContract
from databuilder.contracts.constraints import (
    FirstOfMonthConstraint,
    NotNullConstraint,
    UniqueConstraint,
)


class Patients(TableContract):
    patient_id = Column(
        type=types.PseudoPatientId(),
        constraints=[NotNullConstraint(), UniqueConstraint()],
    )
    height = Column(
        type=types.Float(),
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
        type=types.Float(),
    )


class Tests(TableContract):
    patient_id = Column(
        type=types.PseudoPatientId(),
    )
    result = Column(
        type=types.Boolean(),
    )
    test_date = Column(
        type=types.Date(),
    )
