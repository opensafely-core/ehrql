import databuilder.tables.beta.databricks
import databuilder.tables.beta.smoketest

from ..query_engines.spark import SparkQueryEngine
from .base import BaseBackend, MappedTable, QueryTable


class DatabricksBackend(BaseBackend):
    """Backend for working with data in Databricks."""

    query_engine_class = SparkQueryEngine
    patient_join_column = "patient_id"
    implements = [databuilder.tables.beta.databricks, databuilder.tables.beta.smoketest]

    patients = QueryTable(
        # We're not (currently) provided with a patient table so we have to
        # synthesize one by grabbing all the unique patients with their dates
        # of birth from the prescriptions table. This obviously means that we
        # don't know about patients which have never been prescribed a med.
        # This is OK for our intial purposes.
        """
        SELECT
            Person_ID AS patient_id, MAX(PatientDoB) AS date_of_birth
        FROM
            PCAREMEDS.pcaremeds
        GROUP BY
            Person_ID
        """
    )

    prescriptions = MappedTable(
        source="pcaremeds",
        schema="PCAREMEDS",
        columns=dict(
            patient_id="Person_ID",
            prescribed_dmd_code="PrescribeddmdCode",
            processing_date="ProcessingPeriodDate",
        ),
    )

    hospital_admissions = QueryTable(
        # HES data comes in distinct tables for each financial year which we
        # union together to pretend its a single table.
        "\nUNION ALL\n".join(
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
                apc.ADMIMETH AS admission_method,
                apc.FAE AS episode_is_finished,
                apc_otr.SUSSPELLID AS spell_id
            FROM
                HES_AHAS.hes_apc_{year} AS apc
            JOIN
                HES_AHAS_MPS.hes_apc_{year} AS mps
            ON
                apc.EPIKEY = mps.EPIKEY
            LEFT JOIN
                HES_AHAS.hes_apc_otr_{year} AS apc_otr
            ON
                apc.EPIKEY = apc_otr.EPIKEY
            """
            # "1920" means "Financial year 2019/2020". We only have the one
            # year in the sample data for now but we're anticipating more.
            for year in ["1920"]
        )
    )
