from .contracts import tables

clinical_events = tables.WIP_ClinicalEvents.build_dsl_frame()
hospitalizations = tables.WIP_Hospitalizations.build_dsl_frame()
patient_addresses = tables.WIP_PatientAddress.build_dsl_frame()
patients = tables.WIP_SimplePatientDemographics.build_dsl_frame()
practice_registrations = tables.WIP_PracticeRegistrations.build_dsl_frame()
sgss_sars_cov_2 = tables.WIP_TestResults.build_dsl_frame()
