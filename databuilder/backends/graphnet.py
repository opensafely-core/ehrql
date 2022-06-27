from ..contracts import contracts
from ..query_engines.mssql import MSSQLQueryEngine
from .base import BaseBackend, Column, MappedTable


class GraphnetBackend(BaseBackend):
    """Backend for working with data in Graphnet."""

    query_engine_class = MSSQLQueryEngine
    patient_join_column = "Patient_ID"

    patient_demographics = MappedTable(
        implements=contracts.PatientDemographics,
        source="TRE.Patients",
        columns=dict(
            sex=Column("varchar", source="Sex"),
            date_of_birth=Column("date", source="DateOfBirth"),
            date_of_death=Column("date", source="DateOfDeath"),
        ),
    )

    clinical_events = MappedTable(
        implements=contracts.WIP_ClinicalEvents,
        source="TRE.ClinicalEvents",
        columns=dict(
            code=Column("varchar", source="Code"),
            system=Column("varchar", source="CodingSystem"),
            date=Column("datetime", source="ConsultationDate"),
            numeric_value=Column("float", source="NumericValue"),
        ),
    )

    practice_registrations = MappedTable(
        implements=contracts.WIP_PracticeRegistrations,
        source="TRE.PracticeRegistrations",
        columns=dict(
            pseudo_id=Column("integer", source="Organisation_ID"),
            nuts1_region_name=Column("varchar", source="Region"),
            date_start=Column("datetime", source="StartDate"),
            date_end=Column("datetime", source="EndDate"),
        ),
    )

    covid_test_results = MappedTable(
        implements=contracts.WIP_CovidTestResults,
        source="TRE.CovidTestResults",
        columns=dict(
            date=Column("date", source="SpecimenDate"),
            positive_result=Column("boolean", source="positive_result"),
        ),
    )

    hospitalizations_without_system = MappedTable(
        implements=contracts.WIP_HospitalizationsWithoutSystem,
        source="TRE.Hospitalisations",
        columns=dict(
            date=Column("date", source="AdmitDate"),
            code=Column("varchar", source="DiagCode"),
        ),
    )

    patient_address = MappedTable(
        implements=contracts.WIP_PatientAddress,
        source="TRE.PatientAddresses",
        columns=dict(
            patientaddress_id=Column("integer", source="PatientAddress_ID"),
            date_start=Column("date", source="StartDate"),
            date_end=Column("date", source="EndDate"),
            index_of_multiple_deprivation_rounded=Column("integer", source="IMD"),
            msoa_code=Column("varchar", source="MSOACode"),
            has_postcode=Column("boolean", source="has_postcode"),
        ),
    )
