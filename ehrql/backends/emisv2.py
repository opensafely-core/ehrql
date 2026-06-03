import logging
import urllib.parse

import ehrql.tables.emisv2
import ehrql.tables.smoketest
from ehrql.backend_admin.emisv2 import cleanup_temp_tables
from ehrql.backends.base import QueryTable, SQLBackend
from ehrql.query_engines.trino import TrinoQueryEngine
from ehrql.query_model import nodes as qm
from ehrql.utils.docs_utils import exclude_from_docs


logger = logging.getLogger(__name__)


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
        ehrql.tables.emisv2,
        ehrql.tables.smoketest,
    ]
    # Map tables we don't expose in the user-facing schema to their query model table node
    internal_tables = {
        "t1oo": qm.SelectPatientTable(
            "t1oo",
            # It doesn't need any columns: it's just a list of patient IDs
            schema=qm.TableSchema(),
        ),
    }

    @classmethod
    def admin_tasks(cls):
        return {"cleanup-temp-tables": cleanup_temp_tables}

    def modify_temp_table_schema(self, temp_table_schema, dsn, environ):
        # EMIS have configured things such that each user has a writable schema whose
        # name matches the username
        parts = urllib.parse.urlparse(dsn)
        return parts.username

    def modify_dataset(self, dataset):
        modification_queries = []
        if "include_t1oo" not in self.permissions:
            # TODO: Add reference to docs, similar to TPP, once available
            logger.info("Applying T1OO filtering")
            modification_queries.append(
                qm.Function.Not(
                    qm.AggregateByPatient.Exists(self.internal_tables["t1oo"])
                )
            )

        new_population = dataset.population
        for modification_query in modification_queries:
            new_population = qm.Function.And(new_population, modification_query)

        return qm.Dataset(
            population=new_population,
            variables=dataset.variables,
            events=dataset.events,
            measures=dataset.measures,
        )

    patients = QueryTable(
        # Note: sex = 'U' (unknown) is a common value and
        # is handled by the ELSE clause
        """
        SELECT
            patient_id AS patient_id,
            CAST(date_of_birth AS date) AS date_of_birth,
            CASE
                WHEN sex = 'M' THEN 'male'
                WHEN sex = 'F' THEN 'female'
                WHEN sex = 'I' THEN 'intersex'
                ELSE 'unknown'
            END AS sex,
            CAST(date_of_death AS date) AS date_of_death
        FROM patient
        """
    )

    clinical_events = QueryTable(
        # Note that we use the observation's effective date here rather than
        # the date of the linked consultation for the observation (which is what
        # we use in TPP). This is not a permanent decision - we may revise the
        # implementation in the future.
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
        # Note that we use the medical issue record's effective date here rather
        # than the date of the linked consultation for the medical issue record
        # (which is what we use in TPP). This is not a permanent decision -
        # we may revise the implementation in the future.
        """
        SELECT
            patient_id,
            CAST(effective_datetime AS date) as date,
            CAST(dmd_product_code_id AS varchar) AS dmd_code
        FROM medication_issue_record
        """
    )

    practice_registrations = QueryTable(
        """
        SELECT
            patient_id AS patient_id,
            CAST(registration_start_datetime AS date) AS start_date,
            CAST(registration_end_datetime AS date) AS end_date
        FROM patient
        """
    )

    addresses = QueryTable(
        """
        SELECT
            patient_id AS patient_id,
            CAST(registration_start_datetime AS date) AS start_date,
            CAST(registration_end_datetime AS date) AS end_date,
            CAST(imd_rounded AS int) AS imd_rounded,
            middle_level_super_output_area AS msoa_code
        FROM patient
        """
    )

    t1oo = QueryTable(
        # is_consent_93c1 is based on a clinical code on the patient's record.
        # The field is false if the patient has a type 1 opt-out, and
        # true or NULL if the patient does not have a type 1 opt-out.
        # See https://docs.partner.emis-x.uk/explorer/opensafely/patient/schema/
        """
        SELECT
            patient_id
        FROM patient
        WHERE
            is_consent_93c1 = false
        """
    )
