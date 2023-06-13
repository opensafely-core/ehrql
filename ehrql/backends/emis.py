import ehrql.tables.beta.core
import ehrql.tables.beta.smoketest
from ehrql.backends.base import BaseBackend, MappedTable
from ehrql.query_engines.sqlite import SQLiteQueryEngine


class EMISBackend(BaseBackend):
    """
    !!! warning
        This backend is still under development and is not ready for production use.
        Projects requiring EMIS data should continue to use the [Cohort
        Extractor](https://docs.opensafely.org/study-def/) tool.

    [EMIS Health](https://www.emishealth.com/) are the devlopers and operators of the
    [EMIS Web](https://www.emishealth.com/products/emis-web) EHR platform. The ehrQL
    EMIS backend provides access to primary care data from EMIS Web, plus data linked
    from other sources.
    """

    display_name = "EMIS"
    # Obviously the completed backend will use a TrinoQueryEngine not SQLite
    query_engine_class = SQLiteQueryEngine
    patient_join_column = "patient_id"
    implements = [
        ehrql.tables.beta.core,
        ehrql.tables.beta.smoketest,
    ]

    patients = MappedTable(
        source="patients",
        columns=dict(
            sex="sex",
            date_of_birth="date_of_birth",
            date_of_death="date_of_death",
        ),
    )

    clinical_events = MappedTable(
        source="clinical_events",
        columns=dict(
            date="date",
            snomedct_code="snomedct_code",
            numeric_value="numeric_value",
        ),
    )

    medications = MappedTable(
        source="medications",
        columns=dict(
            date="date",
            dmd_code="dmd_code",
        ),
    )

    ons_deaths = MappedTable(
        source="ons_deaths",
        columns=dict(
            date="date",
            place="place",
            **{
                f"cause_of_death_{i:02d}": f"cause_of_death_{i:02d}"
                for i in range(1, 16)
            },
        ),
    )
