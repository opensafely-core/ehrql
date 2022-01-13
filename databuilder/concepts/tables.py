from ..dsl import CodeColumn, DateColumn, EventFrame, IdColumn, IntColumn, PatientFrame
from ..query_model import Table


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


class Patients(PatientFrame):
    """Provides demographic information about patients."""

    patient_id = IdColumn("patient_id")
    date_of_birth = DateColumn("date_of_birth")

    def __init__(self):
        super().__init__(Table("patients").first_by("patient_id"))


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


clinical_events = ClinicalEvents()
patients = Patients()
registrations = PracticeRegistrations()

# Stubs
hospitalizations = None
patient_addresses = None
covid_test_results = None
