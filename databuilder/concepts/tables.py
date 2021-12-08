from ..dsl import CodeColumn, DateColumn, EventFrame, IdColumn, IntColumn
from ..query_language import Table
from . import types
from .constraints import FirstOfMonthConstraint, NotNullConstraint, UniqueConstraint
from .table_contract import Column, TableContract


class ClinicalEvents(EventFrame):
    """
    Clinical events recorded by GPs.

    Ideally a record of all relevant clinical events with their code and date.
    """

    code = CodeColumn("code")
    date = DateColumn("date")
    value = IntColumn("value")

    def __init__(self):
        super().__init__(Table("clinical_events"))


class PracticeRegistrations(EventFrame):
    """
    For backends with primary care data, the patient's registered practice.

    Ideally a record of all relevant registrations with their start and end
    date, or the latest registered practice.
    """

    patient_id = IdColumn("patient_id")
    date_start = DateColumn("date_start")
    date_end = DateColumn("date_end")

    def __init__(self):
        super().__init__(Table("practice_registrations"))


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


clinical_events = ClinicalEvents()
patients = PatientDemographics()
registrations = PracticeRegistrations()

# Stubs
hospitalizations = None
patient_addresses = None
sgss_sars_cov_2 = None
