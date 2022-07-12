from databuilder.backends.base import BaseBackend, Column, MappedTable, QueryTable
from databuilder.query_engines.mssql import MSSQLQueryEngine


class TPPBackend(BaseBackend):
    """Backend for working with data in TPP."""

    query_engine_class = MSSQLQueryEngine
    patient_join_column = "Patient_ID"

    patients = MappedTable(
        source="Patient",
        columns=dict(
            sex=Column("varchar", source="Sex"),
            date_of_birth=Column("date", source="DateOfBirth"),
        ),
    )

    vaccinations = QueryTable(
        columns=dict(
            date=Column("date"),
            product_name=Column("varchar"),
            target_disease=Column("varchar"),
        ),
        query="""
            SELECT
                vax.Patient_ID AS patient_id,
                CAST(vax.VaccinationDate AS date) AS date,
                vax.VaccinationName AS product_name,
                ref.VaccinationContent AS target_disease
            FROM Vaccination AS vax
            LEFT JOIN VaccinationReference AS ref
            ON vax.VaccinationName_ID = ref.VaccinationName_ID
        """,
    )

    practice_registrations = QueryTable(
        columns=dict(
            start_date=Column("date"),
            end_date=Column("date"),
            practice_pseudo_id=Column("integer"),
            practice_stp=Column("varchar"),
            practice_nuts1_region_name=Column("varchar"),
        ),
        query="""
            SELECT
                reg.Patient_ID AS patient_id,
                reg.StartDate AS start_date,
                reg.EndDate AS end_date,
                org.Organisation_ID AS practice_pseudo_id,
                org.STPCode AS practice_stp,
                org.Region AS practice_nuts1_region_name
            FROM RegistrationHistory AS reg
            LEFT OUTER JOIN Organisation AS org
            ON reg.Organisation_ID = org.Organisation_ID
        """,
    )

    ons_deaths = MappedTable(
        source="ONS_Deaths",
        columns=dict(
            date=Column("date", source="dod"),
            **{
                f"cause_of_death_{i:02d}": Column("varchar", source=f"ICD100{i:02d}")
                for i in range(1, 16)
            },
        ),
    )

    coded_events = QueryTable(
        columns=dict(
            date=Column("date"),
            snomedct_code=Column("varchar"),
            ctv3_code=Column("varchar"),
            numeric_value=Column("float"),
        ),
        query="""
            SELECT
                Patient_ID AS patient_id,
                CAST(ConsultationDate AS date) AS date,
                NULL AS snomedct_code,
                CTV3Code AS ctv3_code,
                NumericValue AS numeric_value
            FROM CodedEvent
            UNION ALL
            SELECT
                Patient_ID AS patient_id,
                CAST(ConsultationDate AS date) AS date,
                ConceptID AS snomedct_code,
                NULL AS ctv3_code,
                NumericValue AS numeric_value
            FROM CodedEvent_SNOMED
        """,
    )

    medications = QueryTable(
        columns=dict(
            date=Column("date"),
            snomedct_code=Column("varchar"),
        ),
        query="""
            SELECT
                Patient_ID AS patient_id,
                CAST(ConsultationDate AS date) AS date,
                MultilexDrug_ID AS snomedct_code
            FROM MedicationIssue
        """,
    )

    addresses = QueryTable(
        columns=dict(
            address_id=Column("integer"),
            start_date=Column("date"),
            end_date=Column("date"),
            address_type=Column("integer"),
            rural_urban_classification=Column("integer"),
            imd_rounded=Column("integer"),
            msoa_code=Column("varchar"),
            care_home_is_potential_match=Column("boolean"),
            care_home_requires_nursing=Column("boolean"),
            care_home_does_not_require_nursing=Column("boolean"),
        ),
        query="""
            SELECT
                addr.Patient_ID AS patient_id,
                addr.PatientAddress_ID AS address_id,
                addr.StartDate AS start_date,
                addr.EndDate AS end_date,
                addr.AddressType AS address_type,
                addr.RuralUrbanClassificationCode AS rural_urban_classification,
                addr.ImdRankRounded AS imd_rounded,
                addr.MSOACode AS msoa_code,
                CASE
                    WHEN carehm.PatientAddress_ID IS NULL THEN 1
                    ELSE 0
                END AS care_home_is_potential_match,
                carehm.LocationRequiresNursing AS care_home_requires_nursing,
                carehm.LocationDoesNotRequireNursing AS care_home_does_not_require_nursing
            FROM PatientAddress AS addr
            LEFT JOIN PotentialCareHomeAddress AS carehm
            ON addr.PatientAddress_ID = carehm.PatientAddress_ID
        """,
    )

    sgss_covid_all_tests = QueryTable(
        columns=dict(
            specimen_taken_date=Column("date"),
            is_positive=Column("boolean"),
        ),
        query="""
            SELECT
                Patient_ID AS patient_id,
                Specimen_Date AS specimen_taken_date,
                1 AS is_positive
            FROM SGSS_AllTests_Positive
            UNION ALL
            SELECT
                Patient_ID AS patient_id,
                Specimen_Date AS specimen_taken_date,
                0 AS is_positive
            FROM SGSS_AllTests_Negative
        """,
    )

    occupation_on_covid_vaccine_record = QueryTable(
        columns=dict(
            is_healthcare_worker=Column("boolean"),
        ),
        query="""
            SELECT
                Patient_ID AS patient_id,
                1 AS is_healthcare_worker
            FROM HealthCareWorker
        """,
    )

    emergency_care_attendances = QueryTable(
        columns=dict(
            id=Column("integer"),
            arrival_date=Column("date"),
            discharge_destination=Column("varchar"),
            **{f"diagnosis_{i:02d}": Column("varchar") for i in range(1, 25)},
        ),
        query=f"""
            SELECT
                EC.Patient_ID AS patient_id,
                EC.EC_Ident AS id,
                EC.Arrival_Date AS arrival_date,
                EC.Discharge_Destination_SNOMED_CT AS discharge_destination,
                {", ".join(f"diag.EC_Diagnosis_{i:02d} AS diagnosis_{i:02d}" for i in range(1, 25))}
            FROM EC
            LEFT JOIN EC_Diagnosis AS diag
            ON EC.EC_Ident = diag.EC_Ident
        """,
    )

    hospital_admissions = QueryTable(
        columns=dict(
            id=Column("integer"),
            admission_date=Column("date"),
            discharge_date=Column("date"),
            admission_method=Column("varchar"),
            all_diagnoses=Column("varchar"),
            patient_classification=Column("varchar"),
            days_in_critical_care=Column("integer"),
        ),
        query="""
            SELECT
                apcs.Patient_ID AS patient_id,
                apcs.APCS_Ident AS id,
                apcs.Admission_Date AS admission_date,
                apcs.Discharge_Date AS discharge_date,
                apcs.Admission_Method AS admission_method,
                apcs.Der_Diagnosis_All AS all_diagnoses,
                apcs.Patient_Classification AS patient_classification,
                CAST(der.Spell_PbR_CC_Day AS INTEGER) AS days_in_critical_care
            FROM APCS AS apcs
            LEFT JOIN APCS_Der AS der
            ON apcs.APCS_Ident = der.APCS_Ident
        """,
    )
