import ehrql.tables.smoketest
from ehrql.backends.base import QueryTable, SQLBackend
from ehrql.query_engines.trino import TrinoQueryEngine
from ehrql.utils.docs_utils import exclude_from_docs


@exclude_from_docs
class EMISV2Backend(SQLBackend):
    """
    [Optum](https://www.optum.co.uk/) are the developers and operators of the [EMIS
    Web](https://www.emishealth.com/emis-web) EHR platform. The ehrQL EMIS backend
    provides access to primary care data from EMIS Web, plus data linked from other
    sources.
    """

    display_name = "EMISV2"
    query_engine_class = TrinoQueryEngine
    patient_join_column = "patient_id"
    implements = [
        ehrql.tables.smoketest,
    ]

    patients = QueryTable(
        """
        SELECT
            patient_id AS patient_id,
            CAST(date_of_birth AS date) AS date_of_birth,
            CASE
                WHEN sex = 'M' THEN 'male'
                WHEN sex = 'F' THEN 'female'
                WHEN sex = 'I' THEN 'intersex'
                WHEN sex = 'U' THEN 'unknown'
                ELSE 'unknown'
            END AS sex,
            CAST(date_of_death AS date) AS date_of_death
        FROM patient
        """
    )

    clinical_events = QueryTable(
        """
        SELECT
            patient_id,
            CAST(effective_datetime AS date) as date,
            CAST(snomed_concept_id AS varchar) AS snomedct_code,
            CAST(numeric_value AS real) AS numeric_value
        FROM observation
        """
    )

    medications = QueryTable(
        """
        SELECT
            patient_id,
            CAST(effective_datetime AS date) as date,
            CAST(dmd_product_code_id AS varchar) AS dmd_code
        FROM medication_issue_record
        """
    )
