from . import types
from .base import Column, TableContract
from .constraints import FirstOfMonthConstraint, NotNullConstraint, UniqueConstraint


class PatientDemographics(TableContract):
    """Provides demographic information about patients."""

    _name = "patient_demographics"

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


###
# The following contracts have not been through any kind of assurance process!
###


class WIP_ClinicalEvents(TableContract):
    """TODO."""

    _name = "clinical_events"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    code = Column(
        type=types.Code(),
        description="",
        help="",
        constraints=[],
    )
    system = Column(
        type=types.String(),
        description="",
        help="",
        constraints=[],
    )
    date = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )
    numeric_value = Column(
        type=types.Float(),
        description="",
        help="",
        constraints=[],
    )


class WIP_HospitalAdmissions(TableContract):
    """TODO."""

    _name = "hospital_admissions"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    admission_date = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )
    primary_diagnosis = Column(
        type=types.Code(),
        description="",
        help="",
        constraints=[],
    )
    admission_method = Column(
        type=types.Integer(),
        description="",
        help="",
        constraints=[],
    )
    episode_is_finished = Column(
        type=types.Boolean(),
        description="",
        help="",
        constraints=[],
    )
    spell_id = Column(
        type=types.Integer(),
        description="",
        help="",
        constraints=[],
    )


class WIP_Hospitalizations(TableContract):
    """TODO."""

    _name = "hospitalizations"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    code = Column(
        type=types.Code(),
        description="",
        help="",
        constraints=[],
    )
    system = Column(
        type=types.String(),
        description="",
        help="",
        constraints=[],
    )


class WIP_HospitalizationsWithoutSystem(TableContract):
    """TODO."""

    _name = "hospitalizations_without_system"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    code = Column(
        type=types.Code(),
        description="",
        help="",
        constraints=[],
    )


class WIP_PatientAddress(TableContract):
    """TODO."""

    _name = "patient_address"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    patientaddress_id = Column(
        type=types.Integer(),
        description="",
        help="",
        constraints=[],
    )
    date_start = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )
    date_end = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )
    index_of_multiple_deprivation_rounded = Column(
        type=types.Integer(),
        description="",
        help="",
        constraints=[],
    )
    has_postcode = Column(
        type=types.Boolean(),
        description="",
        help="",
        constraints=[],
    )


class WIP_PracticeRegistrations(TableContract):
    """TODO."""

    _name = "practice_registrations"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    pseudo_id = Column(
        type=types.Integer(),
        description="",
        help="",
        constraints=[],
    )
    nuts1_region_name = Column(
        type=types.String(),
        description="",
        help="",
        constraints=[],
    )
    date_start = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )
    date_end = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )


class WIP_Prescriptions(TableContract):
    """TODO."""

    _name = "prescriptions"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    prescribed_dmd_code = Column(
        type=types.Code(),
        description="",
        help="",
        constraints=[],
    )
    processing_date = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )


class WIP_CovidTestResults(TableContract):
    """TODO."""

    _name = "covid_test_results"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[],
    )
    date = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )
    positive_result = Column(
        type=types.Boolean(),
        description="",
        help="",
        constraints=[],
    )


class WIP_SimplePatientDemographics(TableContract):
    """TODO."""

    _name = "patients"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        help="",
        constraints=[UniqueConstraint()],
    )
    date_of_birth = Column(
        type=types.Date(),
        description="",
        help="",
        constraints=[],
    )
