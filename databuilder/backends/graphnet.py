import os

from ..query_engines.mssql import MSSQLQueryEngine
from .base import BaseBackend, Column, MappedTable

SCHEMA = os.environ.get("GRAPHNET_DB_SCHEMA", default="TRE")


class GraphnetBackend(BaseBackend):
    """Backend for working with data in Graphnet."""

    query_engine_class = MSSQLQueryEngine
    patient_join_column = "Patient_ID"

    patient_demographics = MappedTable(
        schema=SCHEMA,
        source="Patients",
        columns=dict(
            sex=Column("varchar", source="Sex"),
            date_of_birth=Column("date", source="DateOfBirth"),
            date_of_death=Column("date", source="DateOfDeath"),
        ),
    )

    clinical_events = MappedTable(
        schema=SCHEMA,
        source="ClinicalEvents",
        columns=dict(
            code=Column("varchar", source="Code"),
            system=Column("varchar", source="CodingSystem"),
            date=Column("datetime", source="ConsultationDate"),
            numeric_value=Column("float", source="NumericValue"),
        ),
    )

    practice_registrations = MappedTable(
        schema=SCHEMA,
        source="PracticeRegistrations",
        columns=dict(
            pseudo_id=Column("integer", source="Organisation_ID"),
            nuts1_region_name=Column("varchar", source="Region"),
            date_start=Column("datetime", source="StartDate"),
            date_end=Column("datetime", source="EndDate"),
        ),
    )

    covid_test_results = MappedTable(
        schema=SCHEMA,
        source="CovidTestResults",
        columns=dict(
            date=Column("date", source="SpecimenDate"),
            positive_result=Column("boolean", source="positive_result"),
        ),
    )

    hospitalizations_without_system = MappedTable(
        schema=SCHEMA,
        source="Hospitalisations",
        columns=dict(
            date=Column("date", source="AdmitDate"),
            code=Column("varchar", source="DiagCode"),
        ),
    )

    patient_address = MappedTable(
        schema=SCHEMA,
        source="PatientAddresses",
        columns=dict(
            patientaddress_id=Column("integer", source="PatientAddress_ID"),
            date_start=Column("date", source="StartDate"),
            date_end=Column("date", source="EndDate"),
            index_of_multiple_deprivation_rounded=Column("integer", source="IMD"),
            msoa_code=Column("varchar", source="MSOACode"),
            has_postcode=Column("boolean", source="has_postcode"),
        ),
    )
