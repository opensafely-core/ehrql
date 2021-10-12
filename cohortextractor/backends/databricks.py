from cohortextractor.backends.base import BaseBackend, Column, MappedTable, QueryTable
from cohortextractor.query_engines.mssql import MssqlQueryEngine


class DatabricksBackend(BaseBackend):
    backend_id = "databricks"
    # This will have to change, obviously, but it will do to start with
    query_engine_class = MssqlQueryEngine
    patient_join_column = "patient_id"

    patients = QueryTable(
        columns=dict(
            date_of_birth=Column("date"),
        ),
        # We're not (currently) provided with a patient table so we have to
        # synthesize one by grabbing all the unique patients with their dates
        # of birth from the prescriptions table. This obviously means that we
        # don't know about patients which have never been prescribed a med.
        # This is OK for our intial purposes.
        query="""
        SELECT
            Person_ID AS patient_id, MAX(PatientDoB) AS date_of_birth
        FROM
            PCAREMEDS_pcaremeds
        GROUP BY
            Person_ID
        """,
    )

    prescriptions = MappedTable(
        source="PCAREMEDS_pcaremeds",
        columns=dict(
            patient_id=Column("integer", source="Person_ID"),
            prescribed_dmd_code=Column(
                "code", source="PrescribeddmdCode", system="dmd"
            ),
            processing_date=Column("date", source="ProcessingPeriodDate"),
        ),
    )

    hospital_admissions = QueryTable(
        columns=dict(
            admission_date=Column("date"),
            primary_diagnosis=Column("code", system="icd10"),
            admission_method=Column("integer"),
            episode_is_finished=Column("boolean"),
            spell_id=Column("integer"),
        ),
        # HES data comes in distinct tables for each financial year which we
        # union together to pretend its a single table.
        query="\nUNION ALL\n".join(
            # We join the APC (Admitted Patient Care) table with the MPS
            # (Master Person Service) table so we can get the associated
            # "person ID" which functions as our unique patient identifier that
            # can be matched with the prescriptions data.
            #
            # We also join with the APC-OTR table (not sure what OTR stands
            # for) using EPIKEY (presumably "episode key") so we can get a
            # "spell ID".
            #
            # A spell corresponds to a single, continuous stay in a single
            # hospital from time of admission (or transfer in from another
            # hospital, or birth) to discharge (or transfer out to another
            # hospital, or death). Within that stay, each continuous period
            # spent under the care of a particular consultant is an "episode".
            # A patient may move around the hospital as their clinical needs
            # change, in which case their single spell in that hospital may be
            # composed of mutiple episodes as they come under the care of
            # different consultants.
            f"""
            SELECT
                mps.PERSON_ID AS patient_id,
                apc.ADMIDATE AS admission_date,
                apc.DIAG_4_01 AS primary_diagnosis,
                apc.ADMINMETH AS admission_method,
                apc.FAE AS episode_is_finished,
                apc_otr.SUSSPELLID AS spell_id
            FROM
                HES_AHAS_hes_apc_{year} AS apc
            JOIN
                HES_AHAS_MPS_hes_apc_{year} AS mps
            ON
                apc.EPIKEY = mps.EPIKEY
            LEFT JOIN
                HES_AHAS_hes_apc_otr_{year} AS apc_otr
            ON
                apc.EPIKEY = apc_otr.EPIKEY
            """
            # "1920" means "Financial year 2019/2020". We only have the one
            # year in the sample data for now but we're anticipating more.
            for year in ["1920"]
        ),
    )
