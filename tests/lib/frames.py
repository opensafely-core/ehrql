from . import contracts

events = contracts.Events.build_dsl_frame()
patients = contracts.Patients.build_dsl_frame()
registrations = contracts.Registrations.build_dsl_frame()
tests = contracts.Tests.build_dsl_frame()
