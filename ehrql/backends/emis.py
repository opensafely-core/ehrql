import ehrql.tables.beta.core
import ehrql.tables.beta.smoketest
from ehrql.backends.base import MappedTable, SQLBackend
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
            underlying_cause_of_death="icd10u",
            **{
                f"cause_of_death_{i:02d}": f"cause_of_death_{i:02d}"
                for i in range(1, 16)
            },
        ),
    )
