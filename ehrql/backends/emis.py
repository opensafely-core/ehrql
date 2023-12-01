import ehrql.tables.beta.core
import ehrql.tables.beta.emis
import ehrql.tables.beta.raw.core
import ehrql.tables.beta.smoketest
from ehrql.backends.base import MappedTable, QueryTable, SQLBackend
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

    ons_deaths_raw = MappedTable(
        source="ons_deaths_raw",
        columns=dict(
            date="date",
            place="place",
            underlying_cause_of_death="icd10u",
            **{
                f"cause_of_death_{i:02d}": f"cause_of_death_{i:02d}"
                for i in range(1, 16)
            },
        ),
    )

    # This is just a placeholder for the EMIS backend
    ons_deaths = MappedTable(
        source="ons_deaths",
        columns=dict(
            date="date",
            place="place",
            underlying_cause_of_death="icd10u",
            **{
                f"cause_of_death_{i:02d}": f"cause_of_death_{i:02d}"
                for i in range(1, 16)
            },
        ),
    )
