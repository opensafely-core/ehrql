import ehrql.tables.beta.core
import ehrql.tables.beta.emis
import ehrql.tables.beta.raw.core
import ehrql.tables.beta.raw.emis
import ehrql.tables.beta.smoketest
from ehrql.backends.base import QueryTable, SQLBackend
from ehrql.query_engines.trino import TrinoQueryEngine


class EMISBackend(SQLBackend):
    """
    !!! warning
        Research access to the backend provided by EMIS is temporarily unavailable,
        pending funding arrangements between NHS England and EMIS.
        When funding has been secured,
        we will publish a timeline for gradually reopening access.

    [EMIS Health](https://www.emishealth.com/) are the developers and operators of the
    [EMIS Web](https://www.emishealth.com/products/emis-web) EHR platform. The ehrQL
    EMIS backend provides access to primary care data from EMIS Web, plus data linked
    from other sources.
    """

    display_name = "EMIS"
    query_engine_class = TrinoQueryEngine
    patient_join_column = "registration_id"
    implements = [
        ehrql.tables.beta.core,
        ehrql.tables.beta.raw.core,
        ehrql.tables.beta.raw.emis,
        ehrql.tables.beta.emis,
        ehrql.tables.beta.smoketest,
    ]

    patients = QueryTable(
        """
        SELECT
            registration_id AS patient_id,
            CASE
                WHEN gender = 1 THEN 'male'
                WHEN gender = 2 THEN 'female'
                ELSE 'unknown'
            END AS sex,
            date_of_birth,
            date_of_death
        FROM patient_all_orgs_v2
        WHERE registration_id NOT IN (
            SELECT registration_id
            FROM patient_all_orgs_v2
            GROUP BY registration_id
            HAVING COUNT(*) > 1
        )
        """,
        implementation_notes=dict(
            sex=(
                "Sex as self-declared or observed. "
                "See https://www.datadictionary.nhs.uk/attributes/person_gender_code.html"
            ),
        ),
    )

    clinical_events = QueryTable(
        """
        SELECT
            registration_id AS patient_id,
            CAST(effective_date AS date) as date,
            CAST(snomed_concept_id AS varchar) AS snomedct_code,
            CAST(value_pq_1 AS real) AS numeric_value
        FROM observation_all_orgs_v2
        """
    )

    medications = QueryTable(
        """
        SELECT
            registration_id AS patient_id,
            CAST(effective_date AS date) as date,
            CAST(snomed_concept_id AS varchar) AS dmd_code
        FROM medication_all_orgs_v2
        """
    )

    # ONS DEATHS
    # The ONS table has no registration_id, so we need to join on the patient
    # table on nhsno to add it in
    patient_table_query = """
        SELECT
            registration_id,
            nhs_no AS nhs_no
        FROM patient_all_orgs_v2
        WHERE registration_id NOT IN (
            SELECT registration_id
            FROM patient_all_orgs_v2
            GROUP BY registration_id
            HAVING COUNT(*) > 1
        )
    """
    # The ONS table is also updated with each release of data from ONS, so we
    # need to filter for just the records which match the most recent upload_date
    ons_table_query = f"""
        SELECT
            p.registration_id as registration_id,
            CAST(date_parse(o.reg_stat_dod, '%Y%m%d') AS date) AS dod,
            o.icd10u,
            o.icd10001,
            o.icd10002,
            o.icd10003,
            o.icd10004,
            o.icd10005,
            o.icd10006,
            o.icd10007,
            o.icd10008,
            o.icd10009,
            o.icd10010,
            o.icd10011,
            o.icd10012,
            o.icd10013,
            o.icd10014,
            o.icd10015
        FROM ons_view o
        JOIN ({patient_table_query}) p ON o.pseudonhsnumber = p.nhs_no
        WHERE o.upload_date = (SELECT MAX(upload_date) FROM ons_view)
    """

    ons_deaths_raw = QueryTable(
        f"""
            SELECT
                registration_id as patient_id,
                dod as date,
                icd10u AS underlying_cause_of_death,
                icd10001 AS cause_of_death_01,
                icd10002 AS cause_of_death_02,
                icd10003 AS cause_of_death_03,
                icd10004 AS cause_of_death_04,
                icd10005 AS cause_of_death_05,
                icd10006 AS cause_of_death_06,
                icd10007 AS cause_of_death_07,
                icd10008 AS cause_of_death_08,
                icd10009 AS cause_of_death_09,
                icd10010 AS cause_of_death_10,
                icd10011 AS cause_of_death_11,
                icd10012 AS cause_of_death_12,
                icd10013 AS cause_of_death_13,
                icd10014 AS cause_of_death_14,
                icd10015 AS cause_of_death_15
            FROM ({ons_table_query})
        """
    )

    ons_deaths = QueryTable(
        f"""
            SELECT
                registration_id as patient_id,
                dod as date,
                icd10u AS underlying_cause_of_death,
                icd10001 AS cause_of_death_01,
                icd10002 AS cause_of_death_02,
                icd10003 AS cause_of_death_03,
                icd10004 AS cause_of_death_04,
                icd10005 AS cause_of_death_05,
                icd10006 AS cause_of_death_06,
                icd10007 AS cause_of_death_07,
                icd10008 AS cause_of_death_08,
                icd10009 AS cause_of_death_09,
                icd10010 AS cause_of_death_10,
                icd10011 AS cause_of_death_11,
                icd10012 AS cause_of_death_12,
                icd10013 AS cause_of_death_13,
                icd10014 AS cause_of_death_14,
                icd10015 AS cause_of_death_15
            FROM (
                SELECT
                    registration_id,
                    dod,
                    icd10u,
                    icd10001,
                    icd10002,
                    icd10003,
                    icd10004,
                    icd10005,
                    icd10006,
                    icd10007,
                    icd10008,
                    icd10009,
                    icd10010,
                    icd10011,
                    icd10012,
                    icd10013,
                    icd10014,
                    icd10015,
                    ROW_NUMBER() OVER (
                        PARTITION BY registration_id
                        ORDER BY dod ASC, icd10u ASC
                    ) AS rownum
                FROM ({ons_table_query})
            ) t
            WHERE t.rownum = 1
        """
    )
