import datetime

from databuilder.query_language import EventFrame, PatientFrame, Series, construct

from .constraints import ChoiceConstraint, FirstOfMonthConstraint, NotNullConstraint


@construct
class patient_demographics(PatientFrame):
    """Provides demographic information about patients."""

    date_of_birth = Series(
        datetime.date,
        description="Patient's year and month of birth, provided in format YYYY-MM-01.",
        constraints=[NotNullConstraint(), FirstOfMonthConstraint()],
    )
    sex = Series(
        str,
        description="Patient's sex.",
        constraints=[
            NotNullConstraint(),
            ChoiceConstraint("female", "male", "intersex", "unknown"),
        ],
    )
    date_of_death = Series(
        datetime.date,
        description="Patient's year and month of death, provided in format YYYY-MM-01.",
        constraints=[FirstOfMonthConstraint()],
    )


###
# The following contracts have not been through any kind of assurance process!
###


@construct
class wip_clinical_events(EventFrame):
    """TODO."""

    __tablename__ = "clinical_events"

    code = Series(str)
    system = Series(str)
    date = Series(datetime.date)
    numeric_value = Series(float)


@construct
class wip_hospital_admissions(EventFrame):
    """TODO."""

    __tablename__ = "hospital_admissions"

    admission_date = Series(datetime.date)
    primary_diagnosis = Series(str)
    admission_method = Series(int)
    episode_is_finished = Series(bool)
    spell_id = Series(int)


@construct
class wip_hospitalizations(EventFrame):
    """TODO."""

    __tablename__ = "hospitalizations"

    date = Series(datetime.date)
    code = Series(str)
    system = Series(str)


@construct
class wip_hospitalizations_without_system(EventFrame):
    """TODO."""

    __tablename__ = "hospitalizations_without_system"

    code = Series(str)


@construct
class wip_patient_address(EventFrame):
    """TODO."""

    __tablename__ = "patient_address"

    patientaddress_id = Series(int)
    date_start = Series(datetime.date)
    date_end = Series(datetime.date)
    index_of_multiple_deprivation_rounded = Series(int)
    has_postcode = Series(bool)


@construct
class wip_practice_registrations(EventFrame):
    """TODO."""

    __tablename__ = "practice_registrations"

    pseudo_id = Series(int)
    nuts1_region_name = Series(str)
    date_start = Series(datetime.date)
    date_end = Series(datetime.date)


@construct
class wip_prescriptions(EventFrame):
    """TODO."""

    __tablename__ = "prescriptions"

    prescribed_dmd_code = Series(str)
    processing_date = Series(datetime.date)


@construct
class wip_covid_test_results(EventFrame):
    """TODO."""

    __tablename__ = "covid_test_results"

    date = Series(datetime.date)
    positive_result = Series(bool)


@construct
class wip_simple_patient_demographics(EventFrame):
    """TODO."""

    __tablename__ = "patients"

    date_of_birth = Series(datetime.date)
