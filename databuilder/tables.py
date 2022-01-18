from .contracts import contracts
from .dsl import (
    BoolColumn,
    CodeColumn,
    DateColumn,
    EventTable,
    FloatColumn,
    IdColumn,
    IntColumn,
    PatientTable,
    StrColumn,
)


class PatientDemographics(PatientTable):
    patient_id = IdColumn("patient_id")
    date_of_birth = DateColumn("date_of_birth")
    sex = StrColumn("sex")
    date_of_death = DateColumn("date_of_death")


patient_demographics = PatientDemographics(contracts.PatientDemographics)


###
# The following frames are based on contracts have not been through any kind of
# assurance process!
###


class WIP_ClinicalEvents(EventTable):
    patient_id = IdColumn("patient_id")
    code = CodeColumn("code")
    system = StrColumn("system")
    date = DateColumn("date")
    numeric_value = FloatColumn("numeric_value")


clinical_events = WIP_ClinicalEvents(contracts.WIP_ClinicalEvents)


class WIP_HospitalAdmissions(EventTable):
    patient_id = IdColumn("patient_id")
    admission_date = DateColumn("admission_date")
    primary_diagnosis = CodeColumn("primary_diagnosis")
    admission_method = IntColumn("admission_method")
    episode_is_finished = BoolColumn("episode_is_finished")
    spell_id = IntColumn("spell_id")


hospital_admissions = WIP_HospitalAdmissions(contracts.WIP_HospitalAdmissions)


class WIP_Hospitalizations(EventTable):
    patient_id = IdColumn("patient_id")
    date = DateColumn("date")
    code = CodeColumn("code")
    system = StrColumn("system")


hospitalizations = WIP_Hospitalizations(contracts.WIP_Hospitalizations)


class WIP_HospitalizationsWithoutSystem(EventTable):
    patient_id = IdColumn("patient_id")
    code = CodeColumn("code")


hospitalizations_without_system = WIP_HospitalizationsWithoutSystem(
    contracts.WIP_HospitalizationsWithoutSystem
)


class WIP_PatientAddress(EventTable):
    patient_id = IdColumn("patient_id")
    patientaddress_id = IntColumn("patientaddress_id")
    date_start = DateColumn("date_start")
    date_end = DateColumn("date_end")
    index_of_multiple_deprivation_rounded = IntColumn(
        "index_of_multiple_deprivation_rounded"
    )
    has_postcode = BoolColumn("has_postcode")


patient_addresses = WIP_PatientAddress(contracts.WIP_PatientAddress)


class WIP_PracticeRegistrations(EventTable):
    patient_id = IdColumn("patient_id")
    pseudo_id = IntColumn("pseudo_id")
    nuts1_region_name = StrColumn("nuts1_region_name")
    date_start = DateColumn("date_start")
    date_end = DateColumn("date_end")


practice_registrations = WIP_PracticeRegistrations(contracts.WIP_PracticeRegistrations)


class WIP_Prescriptions(EventTable):
    patient_id = IdColumn("patient_id")
    prescribed_dmd_code = CodeColumn("prescribed_dmd_code")
    processing_date = DateColumn("processing_date")


prescriptions = WIP_Prescriptions(contracts.WIP_Prescriptions)


class WIP_CovidTestResults(EventTable):
    patient_id = IdColumn("patient_id")
    date = DateColumn("date")
    positive_result = BoolColumn("positive_result")


covid_test_results = WIP_CovidTestResults(contracts.WIP_CovidTestResults)


class WIP_SimplePatientDemographics(PatientTable):
    patient_id = IdColumn("patient_id")
    date_of_birth = DateColumn("date_of_birth")


patients = WIP_SimplePatientDemographics(contracts.WIP_SimplePatientDemographics)
