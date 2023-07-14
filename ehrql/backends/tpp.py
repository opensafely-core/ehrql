import ehrql.tables.beta.core
import ehrql.tables.beta.smoketest
import ehrql.tables.beta.tpp
from ehrql.backends.base import BaseBackend, MappedTable, QueryTable
from ehrql.query_engines.mssql import MSSQLQueryEngine


class TPPBackend(BaseBackend):
    """
    [TPP](https://tpp-uk.com/) are the developers and operators of the
    [SystmOne](https://tpp-uk.com/products/) EHR platform. The ehrQL TPP backend
    provides access to primary care data from SystmOne, plus data linked from other
    sources.
    """

    display_name = "TPP"
    query_engine_class = MSSQLQueryEngine
    patient_join_column = "Patient_ID"
    implements = [
        ehrql.tables.beta.core,
        ehrql.tables.beta.tpp,
        ehrql.tables.beta.smoketest,
    ]

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
                CAST(reg.StartDate AS date) AS start_date,
                CAST(reg.EndDate AS date) AS end_date,
                org.Organisation_ID AS practice_pseudo_id,
                NULLIF(org.STPCode, '') AS practice_stp,
                NULLIF(org.Region, '') AS practice_nuts1_region_name
            FROM RegistrationHistory AS reg
            LEFT OUTER JOIN Organisation AS org
            ON reg.Organisation_ID = org.Organisation_ID
        """
    )

    ons_deaths = MappedTable(
        source="ONS_Deaths",
        columns=dict(
            date="dod",
            place="Place_of_occurrence",
            underlying_cause_of_death="icd10u",
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

    @QueryTable.from_function
    def medications(self):
        temp_database_name = self.config.get(
            "TEMP_DATABASE_NAME", "PLACEHOLDER_FOR_TEMP_DATABASE_NAME"
        )
        return f"""
            SELECT
                meds.Patient_ID AS patient_id,
                CAST(meds.ConsultationDate AS date) AS date,
                COALESCE(NULLIF(dict.DMD_ID, ''), NULLIF(custom_dict.DMD_ID, '')) AS dmd_code
            FROM MedicationIssue AS meds
            LEFT JOIN MedicationDictionary AS dict
            ON meds.MultilexDrug_ID = dict.MultilexDrug_ID
            LEFT JOIN {temp_database_name}..CustomMedicationDictionary AS custom_dict
            ON meds.MultilexDrug_ID = custom_dict.MultilexDrug_ID
        """

    addresses = QueryTable(
        """
            SELECT
                addr.Patient_ID AS patient_id,
                addr.PatientAddress_ID AS address_id,
                CAST(addr.StartDate AS date) AS start_date,
                CAST(addr.EndDate AS date) AS end_date,
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
                CAST(der.Spell_PbR_CC_Day AS INTEGER) AS days_in_critical_care,
                der.Spell_Primary_Diagnosis as primary_diagnoses
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

    ons_cis_raw = MappedTable(
        source="ONS_CIS_New",
        columns=dict(
            covid_admitted="covid_admitted",
            covid_date="covid_date",
            covid_nhs_contact="covid_nhs_contact",
            covid_test_swab="covid_test_swab",
            covid_test_swab_neg_last_date="covid_test_swab_neg_last_date",
            covid_test_swab_pos_first_date="covid_test_swab_pos_first_date",
            covid_test_swab_result="covid_test_swab_result",
            covid_think_havehad="covid_think_havehad",
            ctsgene_result="ctSgene_result",
            health_care_clean="health_care_clean",
            hhsize="hhsize",
            imd_decile_e="imd_decile_E",
            imd_quartile_e="imd_quartile_E",
            last_linkage_dt="last_linkage_dt",
            long_covid_have_symptoms="long_covid_have_symptoms",
            nhs_data_share="nhs_data_share",
            patient_facing_clean="patient_facing_clean",
            result_combined="result_combined",
            result_mk="result_mk",
            result_mk_date="result_mk_date",
            rural_urban="rural_urban",
            think_have_covid_sympt_now="think_have_covid_sympt_now",
            visit_date="visit_date",
            visit_num="visit_num",
            visit_status="visit_status",
            visit_type="visit_type",
        ),
    )

    ons_cis = MappedTable(
        source="ONS_CIS_New",
        columns=dict(
            visit_date="visit_date",
            visit_num="visit_num",
            is_opted_out_of_nhs_data_share="nhs_data_share",
            last_linkage_dt="last_linkage_dt",
            imd_decile_e="imd_decile_E",
            imd_quartile_e="imd_quartile_E",
            rural_urban="rural_urban",
        ),
    )

    isaric_raw = QueryTable(
        """
            SELECT
                Patient_ID as patient_id,
                age,
                "age.factor" AS age_factor,
                calc_age,
                sex,
                ethnic___1,
                ethnic___2,
                ethnic___3,
                ethnic___4,
                ethnic___5,
                ethnic___6,
                ethnic___7,
                ethnic___8,
                ethnic___9,
                ethnic___10,
                covid19_vaccine,
                CASE
                    WHEN covid19_vaccined != 'NA' THEN CONVERT(DATE, covid19_vaccined, 23)
                END AS covid19_vaccined,
                CASE
                    WHEN covid19_vaccine2d != 'NA' THEN CONVERT(DATE, covid19_vaccine2d, 23)
                END AS covid19_vaccine2d,
                covid19_vaccined_nk,
                corona_ieorres,
                coriona_ieorres2,
                coriona_ieorres3,
                inflammatory_mss,
                CASE
                    WHEN cestdat != 'NA' THEN CONVERT(DATE, cestdat, 23)
                END AS cestdat,
                CASE
                    WHEN hostdat != 'NA' THEN CONVERT(DATE, hostdat, 23)
                END AS hostdat,
                CASE
                    WHEN chrincard IN ('YES', 'NO', 'Unknown') THEN chrincard
                    WHEN chrincard = 'NA' THEN 'NO'
                END AS chrincard,
                CASE
                    WHEN hypertension_mhyn IN ('YES', 'NO', 'Unknown') THEN hypertension_mhyn
                    WHEN hypertension_mhyn = 'NA' THEN 'NO'
                END AS hypertension_mhyn,
                CASE
                    WHEN chronicpul_mhyn IN ('YES', 'NO', 'Unknown') THEN chronicpul_mhyn
                    WHEN chronicpul_mhyn = 'NA' THEN 'NO'
                END AS chronicpul_mhyn,
                CASE
                    WHEN asthma_mhyn IN ('YES', 'NO', 'Unknown') THEN asthma_mhyn
                    WHEN asthma_mhyn = 'NA' THEN 'NO'
                END AS asthma_mhyn,
                CASE
                    WHEN renal_mhyn IN ('YES', 'NO', 'Unknown') THEN renal_mhyn
                    WHEN renal_mhyn = 'NA' THEN 'NO'
                END AS renal_mhyn,
                CASE
                    WHEN mildliver IN ('YES', 'NO', 'Unknown') THEN mildliver
                    WHEN mildliver = 'NA' THEN 'NO'
                END AS mildliver,
                CASE
                    WHEN modliv IN ('YES', 'NO', 'Unknown') THEN modliv
                    WHEN modliv = 'NA' THEN 'NO'
                END AS modliv,
                CASE
                    WHEN chronicneu_mhyn IN ('YES', 'NO', 'Unknown') THEN chronicneu_mhyn
                    WHEN chronicneu_mhyn = 'NA' THEN 'NO'
                END AS chronicneu_mhyn,
                CASE
                    WHEN malignantneo_mhyn IN ('YES', 'NO', 'Unknown') THEN malignantneo_mhyn
                    WHEN malignantneo_mhyn = 'NA' THEN 'NO'
                END AS malignantneo_mhyn,
                CASE
                    WHEN chronichaemo_mhyn IN ('YES', 'NO', 'Unknown') THEN chronichaemo_mhyn
                    WHEN chronichaemo_mhyn = 'NA' THEN 'NO'
                END AS chronichaemo_mhyn,
                CASE
                    WHEN aidshiv_mhyn IN ('YES', 'NO', 'Unknown') THEN aidshiv_mhyn
                    WHEN aidshiv_mhyn = 'NA' THEN 'NO'
                END AS aidshiv_mhyn,
                CASE
                    WHEN obesity_mhyn IN ('YES', 'NO', 'Unknown') THEN obesity_mhyn
                    WHEN obesity_mhyn = 'NA' THEN 'NO'
                END AS obesity_mhyn,
                diabetes_type_mhyn,
                CASE
                    WHEN diabetescom_mhyn IN ('YES', 'NO', 'Unknown') THEN diabetescom_mhyn
                    WHEN diabetescom_mhyn = 'NA' THEN 'NO'
                END AS diabetescom_mhyn,
                CASE
                    WHEN diabetes_mhyn IN ('YES', 'NO', 'Unknown') THEN diabetes_mhyn
                    WHEN diabetes_mhyn = 'NA' THEN 'NO'
                END AS diabetes_mhyn,
                CASE
                    WHEN rheumatologic_mhyn IN ('YES', 'NO', 'Unknown') THEN rheumatologic_mhyn
                    WHEN rheumatologic_mhyn = 'NA' THEN 'NO'
                END AS rheumatologic_mhyn,
                CASE
                    WHEN dementia_mhyn IN ('YES', 'NO', 'Unknown') THEN dementia_mhyn
                    WHEN dementia_mhyn = 'NA' THEN 'NO'
                END AS dementia_mhyn,
                CASE
                    WHEN malnutrition_mhyn IN ('YES', 'NO', 'Unknown') THEN malnutrition_mhyn
                    WHEN malnutrition_mhyn = 'NA' THEN 'NO'
                END AS malnutrition_mhyn,
                smoking_mhyn,
                hooccur,
                CASE
                    WHEN hostdat_transfer != 'NA' THEN CONVERT(DATE, hostdat_transfer, 23)
                END AS hostdat_transfer,
                hostdat_transfernk,
                readm_cov19,
                CASE
                    WHEN dsstdat != 'NA' THEN CONVERT(DATE, dsstdat, 23)
                END AS dsstdat,
                CASE
                    WHEN dsstdtc != 'NA' THEN CONVERT(DATE, dsstdtc, 23)
                END AS dsstdtc
            FROM ISARIC_New
        """
    )

    open_prompt = QueryTable(
        """
        SELECT
            Patient_ID AS patient_id,
            CASE
                WHEN CodeSystemId = 0 THEN ConceptId
            END AS snomedct_code,
            CASE
                WHEN CodeSystemId = 2 THEN ConceptId
            END ctv3_code,
            CAST(CreationDate AS date) AS creation_date,
            CAST(ConsultationDate AS date) AS consultation_date,
            Consultation_ID AS consultation_id,
            CASE
                WHEN NumericCode = 1 THEN NumericValue
            END AS numeric_value
        FROM OpenPROMPT
    """
    )

    apcs_cost = QueryTable(
        """
        SELECT
            cost.Patient_ID AS patient_id,
            cost.APCS_Ident AS apcs_ident,
            cost.Grand_Total_Payment_MFF AS grand_total_payment_mff,
            cost.Tariff_Initial_Amount AS tariff_initial_amount,
            cost.Tariff_Total_Payment AS tariff_total_payment,
            apcs.Admission_Date AS admission_date,
            apcs.Discharge_Date AS discharge_date
        FROM APCS_Cost AS cost
        LEFT JOIN APCS AS apcs
        ON cost.APCS_Ident = apcs.APCS_Ident
    """
    )

    ec_cost = QueryTable(
        """
        SELECT
            cost.Patient_ID AS patient_id,
            cost.EC_Ident AS ec_ident,
            cost.Grand_Total_Payment_MFF AS grand_total_payment_mff,
            cost.Tariff_Total_Payment AS tariff_total_payment,
            ec.Arrival_Date AS arrival_date,
            ec.EC_Decision_To_Admit_Date AS ec_decision_to_admit_date,
            ec.EC_Injury_Date AS ec_injury_date
        FROM EC_Cost AS cost
        LEFT JOIN EC AS ec
        ON cost.EC_Ident = ec.EC_Ident
    """
    )

    opa_cost = QueryTable(
        """
        SELECT
            cost.Patient_ID AS patient_id,
            cost.OPA_Ident AS opa_ident,
            cost.Tariff_OPP AS tariff_opp,
            cost.Grand_Total_Payment_MFF AS grand_total_payment_mff,
            cost.Tariff_Total_Payment AS tariff_total_payment,
            opa.Appointment_Date AS appointment_date,
            opa.Referral_Request_Received_Date AS referral_request_received_date
        FROM OPA_Cost AS cost
        LEFT JOIN OPA AS opa
        ON cost.OPA_Ident = opa.OPA_Ident
    """
    )

    opa_diag = QueryTable(
        """
        SELECT
            diag.Patient_ID AS patient_id,
            diag.OPA_Ident AS opa_ident,
            diag.Primary_Diagnosis_Code AS primary_diagnosis_code,
            diag.Primary_Diagnosis_Code_Read AS primary_diagnosis_code_read,
            diag.Secondary_Diagnosis_Code_1 AS secondary_diagnosis_code_1,
            diag.Secondary_Diagnosis_Code_1_Read AS secondary_diagnosis_code_1_read,
            opa.Appointment_Date AS appointment_date,
            opa.Referral_Request_Received_Date AS referral_request_received_date
        FROM OPA_Diag AS diag
        LEFT JOIN OPA AS opa
        ON diag.OPA_Ident = opa.OPA_Ident
    """
    )

    opa_proc = QueryTable(
        """
        SELECT
            Patient_ID AS patient_id,
            OPA_Ident AS opa_ident,
            Primary_Procedure_Code AS primary_procedure_code,
            Primary_Procedure_Code_Read AS primary_procedure_code_read,
            Procedure_Code_2 AS procedure_code_1,
            Procedure_Code_2_Read AS procedure_code_2_read
        FROM OPA_Proc
    """
    )
