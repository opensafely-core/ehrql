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
        constraints=[NotNullConstraint(), UniqueConstraint()],
    )
    date_of_birth = Column(
        type=types.Date(),
        description="Patient's year and month of birth, provided in format YYYY-MM-01.",
        constraints=[NotNullConstraint(), FirstOfMonthConstraint()],
    )
    sex = Column(
        type=types.Choice("female", "male", "intersex", "unknown"),
        description="Patient's sex.",
        constraints=[NotNullConstraint()],
    )
    date_of_death = Column(
        type=types.Date(),
        description="Patient's year and month of death, provided in format YYYY-MM-01.",
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
        constraints=[],
    )
    code = Column(
        type=types.Code(),
        description="",
        constraints=[],
    )
    system = Column(
        type=types.String(),
        description="",
        constraints=[],
    )
    date = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
    numeric_value = Column(
        type=types.Float(),
        description="",
        constraints=[],
    )


class WIP_HospitalAdmissions(TableContract):
    """TODO."""

    _name = "hospital_admissions"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[],
    )
    admission_date = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
    primary_diagnosis = Column(
        type=types.Code(),
        description="",
        constraints=[],
    )
    admission_method = Column(
        type=types.Integer(),
        description="",
        constraints=[],
    )
    episode_is_finished = Column(
        type=types.Boolean(),
        description="",
        constraints=[],
    )
    spell_id = Column(
        type=types.Integer(),
        description="",
        constraints=[],
    )


class WIP_Hospitalizations(TableContract):
    """TODO."""

    _name = "hospitalizations"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[],
    )
    date = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
    code = Column(
        type=types.Code(),
        description="",
        constraints=[],
    )
    system = Column(
        type=types.String(),
        description="",
        constraints=[],
    )


class WIP_HospitalizationsWithoutSystem(TableContract):
    """TODO."""

    _name = "hospitalizations_without_system"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[],
    )
    code = Column(
        type=types.Code(),
        description="",
        constraints=[],
    )


class WIP_PatientAddress(TableContract):
    """TODO."""

    _name = "patient_address"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[],
    )
    patientaddress_id = Column(
        type=types.Integer(),
        description="",
        constraints=[],
    )
    date_start = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
    date_end = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
    index_of_multiple_deprivation_rounded = Column(
        type=types.Integer(),
        description="",
        constraints=[],
    )
    has_postcode = Column(
        type=types.Boolean(),
        description="",
        constraints=[],
    )


class WIP_PracticeRegistrations(TableContract):
    """TODO."""

    _name = "practice_registrations"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[],
    )
    pseudo_id = Column(
        type=types.Integer(),
        description="",
        constraints=[],
    )
    nuts1_region_name = Column(
        type=types.String(),
        description="",
        constraints=[],
    )
    date_start = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
    date_end = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )


class WIP_Prescriptions(TableContract):
    """TODO."""

    _name = "prescriptions"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[],
    )
    prescribed_dmd_code = Column(
        type=types.Code(),
        description="",
        constraints=[],
    )
    processing_date = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )


class WIP_CovidTestResults(TableContract):
    """TODO."""

    _name = "covid_test_results"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[],
    )
    date = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
    positive_result = Column(
        type=types.Boolean(),
        description="",
        constraints=[],
    )


class WIP_SimplePatientDemographics(TableContract):
    """TODO."""

    _name = "patients"

    patient_id = Column(
        type=types.PseudoPatientId(),
        description="",
        constraints=[UniqueConstraint()],
    )
    date_of_birth = Column(
        type=types.Date(),
        description="",
        constraints=[],
    )
