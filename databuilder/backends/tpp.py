import databuilder.tables.beta.smoketest
import databuilder.tables.beta.tpp
from databuilder.backends.base import BaseBackend, MappedTable, QueryTable
from databuilder.query_engines.mssql import MSSQLQueryEngine


class TPPBackend(BaseBackend):
    """Backend for working with data in TPP."""

    query_engine_class = MSSQLQueryEngine
    patient_join_column = "Patient_ID"
    implements = [databuilder.tables.beta.tpp, databuilder.tables.beta.smoketest]

    patients = QueryTable(
        """
            SELECT
                Patient_ID as patient_id,
                DateOfBirth as date_of_birth,
                CASE
                    WHEN Sex = 'M' THEN 'male'
                    WHEN Sex = 'F' THEN 'female'
                    WHEN Sex = 'I' THEN 'intersex'
                    ELSE 'unknown'
                END AS sex,
                CASE
                    WHEN DateOfDeath != '99991231' THEN DateOfDeath
                END As date_of_death
            FROM Patient
        """,
        implementation_notes=dict(
            sex="Sex assigned at birth.",
        ),
    )

    vaccinations = QueryTable(
        """
            SELECT
                vax.Patient_ID AS patient_id,
                vax.Vaccination_ID AS vaccination_id,
                CAST(vax.VaccinationDate AS date) AS date,
                vax.VaccinationName AS product_name,
                ref.VaccinationContent AS target_disease
            FROM Vaccination AS vax
            LEFT JOIN VaccinationReference AS ref
            ON vax.VaccinationName_ID = ref.VaccinationName_ID
        """
    )

    practice_registrations = QueryTable(
        """
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
        """
    )

    ons_deaths = MappedTable(
        source="ONS_Deaths",
        columns=dict(
            date="dod",
            **{f"cause_of_death_{i:02d}": f"ICD100{i:02d}" for i in range(1, 16)},
        ),
    )

    clinical_events = QueryTable(
        """
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
        """
    )

    medications = QueryTable(
        """
            SELECT
                meds.Patient_ID AS patient_id,
                CAST(meds.ConsultationDate AS date) AS date,
                dict.DMD_ID AS dmd_code,
                meds.MultilexDrug_ID AS multilex_code
            FROM MedicationIssue AS meds
            LEFT JOIN MedicationDictionary AS dict
            ON meds.MultilexDrug_ID = dict.MultilexDrug_ID
        """
    )

    addresses = QueryTable(
        """
            SELECT
                addr.Patient_ID AS patient_id,
                addr.PatientAddress_ID AS address_id,
                addr.StartDate AS start_date,
                addr.EndDate AS end_date,
                addr.AddressType AS address_type,
                addr.RuralUrbanClassificationCode AS rural_urban_classification,
                addr.ImdRankRounded AS imd_rounded,
                CASE
                    WHEN addr.MSOACode NOT IN ('NPC', '') THEN addr.MSOACode
                END AS msoa_code,
                CASE
                    WHEN addr.MSOACode NOT IN ('NPC', '') THEN 1
                    ELSE 0
                END AS has_postcode,
                CASE
                    WHEN carehm.PatientAddress_ID IS NOT NULL THEN 1
                    ELSE 0
                END AS care_home_is_potential_match,
                CASE
                    WHEN carehm.LocationRequiresNursing = 'Y' THEN 1
                    WHEN carehm.LocationRequiresNursing = 'N' THEN 0
                 END AS care_home_requires_nursing,
                CASE
                    WHEN carehm.LocationDoesNotRequireNursing = 'Y' THEN 1
                    WHEN carehm.LocationDoesNotRequireNursing = 'N' THEN 0
                 END AS care_home_does_not_require_nursing
            FROM PatientAddress AS addr
            LEFT JOIN PotentialCareHomeAddress AS carehm
            ON addr.PatientAddress_ID = carehm.PatientAddress_ID
        """
    )

    sgss_covid_all_tests = QueryTable(
        """
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
        """
    )

    occupation_on_covid_vaccine_record = QueryTable(
        """
            SELECT
                Patient_ID AS patient_id,
                1 AS is_healthcare_worker
            FROM HealthCareWorker
        """
    )

    emergency_care_attendances = QueryTable(
        f"""
            SELECT
                EC.Patient_ID AS patient_id,
                EC.EC_Ident AS id,
                EC.Arrival_Date AS arrival_date,
                EC.Discharge_Destination_SNOMED_CT AS discharge_destination,
                {", ".join(f"diag.EC_Diagnosis_{i:02d} AS diagnosis_{i:02d}" for i in range(1, 25))}
            FROM EC
            LEFT JOIN EC_Diagnosis AS diag
            ON EC.EC_Ident = diag.EC_Ident
        """
    )

    hospital_admissions = QueryTable(
        """
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
        """
    )

    appointments = QueryTable(
        # WARNING: There are duplicate rows in the Appointment table, so we add DISTINCT
        # to remove them from this query. When they are removed from the Appointment
        # table, then we will remove DISTINCT from this query.
        """
            SELECT DISTINCT
                Appointment_ID AS appointment_id,
                Patient_ID AS patient_id,
                CAST(BookedDate AS date) AS booked_date,
                CAST(StartDate AS date) AS start_date
            FROM Appointment
        """
    )

    household_memberships_2020 = QueryTable(
        """
            SELECT
                mb.Patient_ID AS patient_id,
                hh.Household_ID AS household_pseudo_id,
                hh.HouseholdSize AS household_size
            FROM HouseholdMember AS mb
            LEFT JOIN Household AS hh
            ON mb.Household_ID = hh.Household_ID
        """
    )

    ons_cis = MappedTable(
        source="ONS_CIS_New",
        columns=dict(
            visit_date="visit_date",
            visit_num="visit_num",
            is_opted_out_of_nhs_data_share="nhs_data_share",
            last_linkage_dt="last_linkage_dt",
        ),
    )

    isaric_raw = MappedTable(
        source="ISARIC_New",
        columns=dict(
            age="age",
            age_factor="age.factor",
            calc_age="calc_age",
            sex="sex",
            ethnic="ethnic",
            corona_ieorres="corona_ieorres",
            coriona_ieorres2="coriona_ieorres2",
            coriona_ieorres3="coriona_ieorres3",
            inflammatory_mss="inflammatory_mss",
            covid19_vaccine="covid19_vaccine",
            covid19_vaccined="covid19_vaccined",
            covid19_vaccined_nk="covid19_vaccined_nk",
            hostdat="hostdat",
            readm_cov19="readm_cov19",
            hooccur="hooccur",
            hostdat_transfer="hostdat_transfer",
            hostdat_transfernk="hostdat_transfernk",
        ),
    )
