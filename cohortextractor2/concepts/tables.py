from ..dsl import EventFrame
from ..query_language import Table
from . import types
from .constraints import DateConstraint
from .table_contract import Column, TableContract


class ClinicalEvents(EventFrame):
    code = "code"
    date = "date"

    def __init__(self):
        super().__init__(Table("clinical_events"))


class PracticeRegistrations(EventFrame):
    patient_id = "patient_id"
    date_start = "date_start"
    date_end = "date_end"

    def __init__(self):
        super().__init__(Table("practice_registrations"))


class PatientDemographics(TableContract):
    """
    Provides demographic information about patients
    """

    patient_id = Column(
        type=types.PseudoPatientId(),
        description=(
            "Patient's pseudonymous identifier, for linkage. You should not normally "
            "output or operate on this column"
        ),
        help="",
    )
    date_of_birth = Column(
        type=types.Date(),
        description="Patient's year and month of birth.",
        help="The day will always be the first of the month. Must be present.",
        constraints=[DateConstraint(match_format=["%Y-%m-01"])],
    )
    sex = Column(
        type=types.Choice("female", "male", "intersex", "unknown"),
        description="Patient's sex.",
        help=(
            "One of male, female, intersex or unknown (the last covers all other options,"
            "including but not limited to 'rather not say' and empty/missing values). "
            "Must be present."
        ),
    )


clinical_events = ClinicalEvents()
patients = PatientDemographics()
registrations = PracticeRegistrations()

# Stubs
hospitalizations = None
patient_addresses = None
sgss_sars_cov_2 = None
