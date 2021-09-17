from cohortextractor.backends.base import BaseBackend, Column, MappedTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


class GraphnetBackend(BaseBackend):
    backend_id = "graphnet"
    query_engine_class = MssqlQueryEngine
    patient_join_column = "Patient_ID"

    patients = MappedTable(
        source="TRE.Patients",
        columns=dict(
            sex=Column("varchar", source="Sex"),
            date_of_birth=Column("date", source="DateOfBirth"),
            date_of_death=Column("date", source="DateOfDeath"),
        ),
    )

    clinical_events = MappedTable(
        source="TRE.ClinicalEvents",
        columns=dict(
            code=Column("varchar", source="CTV3Code"),
            date=Column("datetime", source="ConsultationDate"),
            numeric_value=Column("float", source="NumericValue"),
        ),
    )

    clinical_events_snomed = MappedTable(
        source="TRE.ClinicalEvents_Snomed",
        columns=dict(
            code=Column("varchar", source="ConceptID"),
            date=Column("datetime", source="ConsultationDate"),
            numeric_value=Column("float", source="NumericValue"),
        ),
    )

    practice_registrations = MappedTable(
        source="TRE.PracticeRegistrations",
        columns=dict(
            pseudo_id=Column("integer", source="Organisation_ID"),
            nuts1_region_name=Column("varchar", source="Region"),
            date_start=Column("datetime", source="StartDate"),
            date_end=Column("datetime", source="EndDate"),
        ),
    )

    covid_test_results = MappedTable(
        source="TRE.CovidTestResults",
        columns=dict(
            date=Column("date", source="SpecimentDate"),
            positive_result=Column("boolean", source="positive_result"),
        ),
    )

    hospitalizations = MappedTable(
        source="TRE.Hospitalisations",
        columns=dict(
            date=Column("date", source="AdmitDate"),
            code=Column("varchar", source="DiagCode"),
        ),
    )

    patient_address = MappedTable(
        source="TRE.PatientAddresses"
        columns=dict(
            patientaddress_id=Column("integer", source="PatientAddress_ID"),
            date_start=Column("date", source="StartDate"),
            date_end=Column("date", source="EndDate"),
            index_of_multiple_deprivation_rounded=Column("integer", source="IMD"),
            has_postcode=Column("boolean", source="has_postcode"),
        ),
    )
