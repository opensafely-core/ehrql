import ehrql.tables.smoketest
from ehrql.backends.base import QueryTable, SQLBackend
from ehrql.query_engines.trino import TrinoQueryEngine


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
            date_of_birth
        FROM patient
        """
    )
