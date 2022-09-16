import os

import databuilder.tables.beta.graphnet
import databuilder.tables.beta.smoketest

from ..query_engines.mssql import MSSQLQueryEngine
from .base import BaseBackend, MappedTable

SCHEMA = os.environ.get("GRAPHNET_DB_SCHEMA", default="TRE")


class GraphnetBackend(BaseBackend):
    """Backend for working with data in Graphnet."""

    query_engine_class = MSSQLQueryEngine
    patient_join_column = "Patient_ID"
    implements = [databuilder.tables.beta.graphnet, databuilder.tables.beta.smoketest]

    patients = MappedTable(
        schema=SCHEMA,
        source="Patients",
        columns=dict(
            sex="Sex",
            date_of_birth="DateOfBirth",
            date_of_death="DateOfDeath",
        ),
    )

    clinical_events = MappedTable(
        schema=SCHEMA,
        source="ClinicalEvents",
        columns=dict(
            code="Code",
            system="CodingSystem",
            date="ConsultationDate",
            numeric_value="NumericValue",
        ),
    )

    practice_registrations = MappedTable(
        schema=SCHEMA,
        source="PracticeRegistrations",
        columns=dict(
            pseudo_id="Organisation_ID",
            nuts1_region_name="Region",
            date_start="StartDate",
            date_end="EndDate",
        ),
    )

    covid_test_results = MappedTable(
        schema=SCHEMA,
        source="CovidTestResults",
        columns=dict(
            date="SpecimenDate",
            positive_result="positive_result",
        ),
    )

    hospitalizations_without_system = MappedTable(
        schema=SCHEMA,
        source="Hospitalisations",
        columns=dict(
            date="AdmitDate",
            code="DiagCode",
        ),
    )

    patient_address = MappedTable(
        schema=SCHEMA,
        source="PatientAddresses",
        columns=dict(
            patientaddress_id="PatientAddress_ID",
            date_start="StartDate",
            date_end="EndDate",
            index_of_multiple_deprivation_rounded="IMD",
            msoa_code="MSOACode",
            has_postcode="has_postcode",
        ),
    )
