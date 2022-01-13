from .contracts import contracts
from .dsl import (
    BoolColumn,
    CodeColumn,
    DateColumn,
    EventFrame,
    FloatColumn,
    IdColumn,
    IntColumn,
    PatientFrame,
    StrColumn,
)


class PatientDemographics(PatientFrame):
    patient_id = IdColumn("patient_id")
    date_of_birth = DateColumn("date_of_birth")
    sex = StrColumn("sex")
    date_of_death = DateColumn("date_of_death")


patient_demographics = PatientDemographics.from_contract(contracts.PatientDemographics)


###
# The following frames are based on contracts have not been through any kind of
# assurance process!
###


class WIP_ClinicalEvents(EventFrame):
    patient_id = IdColumn("patient_id")
    code = CodeColumn("code")
    system = StrColumn("system")
    date = DateColumn("date")
    numeric_value = FloatColumn("numeric_value")


clinical_events = WIP_ClinicalEvents.from_contract(contracts.WIP_ClinicalEvents)


class WIP_HospitalAdmissions(EventFrame):
    patient_id = IdColumn("patient_id")
    admission_date = DateColumn("admission_date")
    primary_diagnosis = CodeColumn("primary_diagnosis")
    admission_method = IntColumn("admission_method")
    episode_is_finished = BoolColumn("episode_is_finished")
    spell_id = IntColumn("spell_id")


hospital_admissions = WIP_HospitalAdmissions.from_contract(
    contracts.WIP_HospitalAdmissions
)


class WIP_Hospitalizations(EventFrame):
    patient_id = IdColumn("patient_id")
    code = CodeColumn("code")
    system = StrColumn("system")


hospitalizations = WIP_Hospitalizations.from_contract(contracts.WIP_Hospitalizations)


class WIP_HospitalizationsWithoutSystem(EventFrame):
    patient_id = IdColumn("patient_id")
    code = CodeColumn("code")


hospitalizations_ = WIP_HospitalizationsWithoutSystem.from_contract(
    contracts.WIP_HospitalizationsWithoutSystem
)


class WIP_PatientAddress(EventFrame):
    patient_id = IdColumn("patient_id")
    patientaddress_id = IntColumn("patientaddress_id")
    date_start = DateColumn("date_start")
    date_end = DateColumn("date_end")
    index_of_multiple_deprivation_rounded = IntColumn(
        "index_of_multiple_deprivation_rounded"
    )
    has_postcode = BoolColumn("has_postcode")


patient_addresses = WIP_PatientAddress.from_contract(contracts.WIP_PatientAddress)


class WIP_PracticeRegistrations(EventFrame):
    patient_id = IdColumn("patient_id")
    pseudo_id = IntColumn("pseudo_id")
    nuts1_region_name = StrColumn("nuts1_region_name")
    date_start = DateColumn("date_start")
    date_end = DateColumn("date_end")


practice_registrations = WIP_PracticeRegistrations.from_contract(
    contracts.WIP_PracticeRegistrations
)


class WIP_Prescriptions(EventFrame):
    patient_id = IdColumn("patient_id")
    prescribed_dmd_code = CodeColumn("prescribed_dmd_code")
    processing_date = DateColumn("processing_date")


prescriptions = WIP_Prescriptions.from_contract(contracts.WIP_Prescriptions)


class WIP_CovidTestResults(EventFrame):
    patient_id = IdColumn("patient_id")
    date = DateColumn("date")
    positive_result = BoolColumn("positive_result")


covid_test_results = WIP_CovidTestResults.from_contract(contracts.WIP_CovidTestResults)


class WIP_SimplePatientDemographics(PatientFrame):
    patient_id = IdColumn("patient_id")
    date_of_birth = DateColumn("date_of_birth")


patients = WIP_SimplePatientDemographics.from_contract(
    contracts.WIP_SimplePatientDemographics
)
