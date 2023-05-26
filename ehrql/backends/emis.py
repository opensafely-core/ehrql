import ehrql.tables.beta.core
import ehrql.tables.beta.smoketest
from ehrql.backends.base import BaseBackend, MappedTable
from ehrql.query_engines.sqlite import SQLiteQueryEngine


class EMISBackend(BaseBackend):
    """
    NOTE: This is a PLACEHOLDER in advance of completing work on the EMISBackend
    """

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
