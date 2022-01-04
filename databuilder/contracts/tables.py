from . import types
from .base import Column, TableContract
from .constraints import FirstOfMonthConstraint, NotNullConstraint, UniqueConstraint


class PatientDemographics(TableContract):
    """Provides demographic information about patients."""

    patient_id = Column(
        type=types.PseudoPatientId(),
        description=(
            "Patient's pseudonymous identifier, for linkage. You should not normally "
            "output or operate on this column"
        ),
        help="",
        constraints=[NotNullConstraint(), UniqueConstraint()],
    )
    date_of_birth = Column(
        type=types.Date(),
        description="Patient's year and month of birth, provided in format YYYY-MM-01.",
        help="The day will always be the first of the month. Must be present.",
        constraints=[NotNullConstraint(), FirstOfMonthConstraint()],
    )
    sex = Column(
        type=types.Choice("female", "male", "intersex", "unknown"),
        description="Patient's sex.",
        help=(
            "One of male, female, intersex or unknown (the last covers all other options,"
            "including but not limited to 'rather not say' and empty/missing values). "
            "Must be present."
        ),
        constraints=[NotNullConstraint()],
    )
    date_of_death = Column(
        type=types.Date(),
        description="Patient's year and month of death, provided in format YYYY-MM-01.",
        help="The day will always be the first of the month.",
        constraints=[FirstOfMonthConstraint()],
    )


patient_demographics = PatientDemographics()
